from flask import Flask, request, jsonify
import requests
from db import SessionLocal, Message

# Функция для сохранения сообщения
def save_message(sender, content):
    db = SessionLocal()
    try:
        message = Message(sender=sender, content=content)
        db.add(message)
        db.commit()
        print(f"Сообщение сохранено: {sender} - {content}")  # Логирование
    except Exception as e:
        print(f"Ошибка сохранения сообщения: {e}")
    finally:
        db.close()

# Функция для загрузки всех сообщений
def get_all_messages():
    db = SessionLocal()
    try:
        messages = db.query(Message).order_by(Message.timestamp).all()
        print(f"Загружено {len(messages)} сообщений")  # Логирование
        return messages
    except Exception as e:
        print(f"Ошибка загрузки сообщений: {e}")
        return []
    finally:
        db.close()
app = Flask(__name__)

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

@app.route('/messages', methods=['GET'])
def get_messages():
    # Получить все сообщения из базы данных
    messages = get_all_messages()
    return jsonify([{"sender": msg.sender, "content": msg.content, "timestamp": msg.timestamp.isoformat()} for msg in messages])

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    # Сохранение сообщения пользователя
    save_message(sender="user", content=user_message)

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
        save_message(sender="ai", content=ai_response)

        return jsonify({'response': ai_response})
    else:
        return jsonify({'response': f"Ошибка: {response.status_code} - {response.text}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
