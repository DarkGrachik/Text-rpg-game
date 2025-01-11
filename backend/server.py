from flask import Flask, request, jsonify
import requests
from db import SessionLocal, Message, Chat

app = Flask(__name__) 

# Функция для сохранения чата
def save_chat(title):
    db = SessionLocal()
    try:
        chat = Chat(title=title)
        db.add(chat)
        db.commit()
        db.refresh(chat) 
        print(f"Чат сохранен: {title}")  # Логирование
        return chat
    except Exception as e:
        print(f"Ошибка сохранения чата: {e}")
        db.rollback()
        return None
    finally:
        db.close()

# Функция для сохранения сообщения
def save_message(chat_id, sender, content):
    db = SessionLocal()
    try:
        message = Message(chat_id=chat_id, sender=sender, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        print(f"Сообщение сохранено: {sender} - {content} - {chat_id}")  # Логирование
        return message
    except Exception as e:
        print(f"Ошибка сохранения сообщения: {e}")
        db.rollback()
        return None
    finally:
        db.close()

# Функция для загрузки всех чатов
def get_all_chats():
    db = SessionLocal()
    try:
        chats = db.query(Chat).filter(Chat.deleted == False).all()  # Загружаем только не удаленные чаты
        print(f"Загружено {len(chats)} чатов")  # Логирование
        return chats
    except Exception as e:
        print(f"Ошибка загрузки чатов: {e}")
        return []
    finally:
        db.close()


# Функция для загрузки сообщений по чату
def get_messages_by_chat(chat_id):
    db = SessionLocal()
    try:
        messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.timestamp).all()
        print(f"Загружено {len(messages)} сообщений для чата {chat_id}")  # Логирование
        return messages
    except Exception as e:
        print(f"Ошибка загрузки сообщений: {e}")
        return []
    finally:
        db.close()

# Конфигурация для API Gigachat
GIGACHAT_AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
AUTH_HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': 'b5099afa-5b67-44e6-b1b2-a82ea4fa7d00',
    'Authorization': 'Basic ODlkYTUyYzAtOGJmZC00NDAyLTlkNzYtZDYzZWY0N2ZkMTA1OjYzZmU1OTI0LWFmZGQtNDU0Ny1hNDVjLTYwZWVhMGYzN2Y0Yg=='
}

# Получение токена доступа
def get_access_token():
    payload = {'scope': 'GIGACHAT_API_PERS'}
    response = requests.post(GIGACHAT_AUTH_URL, headers=AUTH_HEADERS, data=payload, verify=False)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error getting access token: {response.status_code} - {response.text}")
        return None

@app.route('/chats', methods=['GET'])
def get_chats():
    chats = get_all_chats()
    return jsonify([{"id": chat.id, "title": chat.title, "created_at": chat.created_at.isoformat()} for chat in chats])

@app.route('/chats', methods=['POST'])
def create_chat():
    data = request.get_json()
    title = data.get('title', '')
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    chat = save_chat(title)
    if chat:
        return jsonify({"id": chat.id, "title": chat.title, "created_at": chat.created_at.isoformat()}), 201
    else:
        return jsonify({'error': 'Failed to create chat'}), 500
    
@app.route('/messages/<int:chat_id>', methods=['GET'])
def get_messages(chat_id):
    messages = get_messages_by_chat(chat_id)
    return jsonify([{
        "sender": msg.sender,
        "content": msg.content,
        "timestamp": msg.timestamp.isoformat()
    } for msg in messages])

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    chat_id = data.get('chat_id')

    # Сохранение сообщения пользователя
    save_message(chat_id=chat_id, sender="user", content=user_message)


    # Получение токена
    access_token = get_access_token()
    if not access_token:
        return jsonify({'response': 'Ошибка авторизации.'}), 500

    # Запрос к Gigachat
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    payload = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": user_message}],
        "n": 1,
        "stream": False,
        "max_tokens": 512,
        "repetition_penalty": 1,
        "update_interval": 0
    }
    response = requests.post(GIGACHAT_API_URL, headers=headers, json=payload, verify=False)
    
    if response.status_code == 200:
        response_data = response.json()
        ai_response = response_data.get('choices', [{}])[0].get('message', {}).get('content', 'Нет ответа.')
        
        # Сохранение ответа ИИ
        save_message(chat_id=chat_id, sender="ai", content=ai_response)

        return jsonify({'response': ai_response})
    else:
        return jsonify({'response': f"Ошибка: {response.status_code} - {response.text}"}), 500

@app.route('/chats/<int:chat_id>/delete', methods=['POST'])
def delete_chat(chat_id):
    db = SessionLocal()
    try:
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            chat.deleted = True
            db.commit()
            return jsonify({'message': f'Чат {chat_id} успешно удален.'}), 200
        else:
            return jsonify({'error': 'Чат не найден.'}), 404
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Ошибка удаления чата: {e}'}), 500
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
