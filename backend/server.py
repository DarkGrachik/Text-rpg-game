from flask import Flask, request, jsonify
import requests
from db import SessionLocal, Message, Chat, Character
from flask_cors import CORS
import json
import re


app = Flask(__name__)
CORS(app, supports_credentials=True)


# Функция для сохранения чата
def save_chat(data):
    db = SessionLocal()
    try:
        chat = Chat(
            title=data.get("title"),
            name=data.get("name"),
            character_class=data.get("character_class"),
            race=data.get("race"),
            level=data.get("level"),
            strength=data.get("strength"),
            dexterity=data.get("dexterity"),
            constitution=data.get("constitution"),
            intelligence=data.get("intelligence"),
            wisdom=data.get("wisdom"),
            charisma=data.get("charisma"),
            appearance=data.get("appearance"),
            background=data.get("background")
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
        print(f"Чат сохранен: {chat.title}")
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

# Функция для загрузки всех персонажей
def get_all_characters():
    db = SessionLocal()
    try:
        characters = db.query(Character).filter(Character.deleted == False).all()  # Загружаем только не удаленные чаты
        print(f"Загружено {len(characters)} персонажей")  # Логирование
        return characters
    except Exception as e:
        print(f"Ошибка загрузки персонажей: {e}")
        return []
    finally:
        db.close()

def save_character(data):
    db = SessionLocal()
    try:
        character = Character(
            name=data.get('name', ''),
            character_class=data.get('character_class', ''),
            race=data.get('race', ''),
            strength=data.get('strength', 0),
            dexterity=data.get('dexterity', 0),
            constitution=data.get('constitution', 0),
            intelligence=data.get('intelligence', 0),
            wisdom=data.get('wisdom', 0),
            charisma=data.get('charisma', 0),
            level=data.get('level', 1),
            appearance=data.get('appearance', ''),
            background=data.get('background', '')
        )
        db.add(character)
        db.commit()
        db.refresh(character)
        print(f"Персонаж сохранен: {character.name}")
        return character
    except Exception as e:
        print(f"Ошибка сохранения персонажа: {e}")
        db.rollback()
        return None
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
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    chat = save_chat(data)
    if chat:
        return jsonify({
            "id": chat.id,
            "title": chat.title,
            "created_at": chat.created_at.isoformat()
        }), 201
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

    db = SessionLocal()
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        db.close()
        return jsonify({'response': 'Чат не найден.'}), 404

    character_info = (
        f"Имя: {chat.name}, "
        f"Класс: {chat.character_class}, "
        f"Раса: {chat.race}, "
        f"Сила: {chat.strength}, Ловкость: {chat.dexterity}, Телосложение: {chat.constitution}, "
        f"Интеллект: {chat.intelligence}, Мудрость: {chat.wisdom}, Харизма: {chat.charisma}, "
        f"Уровень: {chat.level}\n"
        f"Внешность: {chat.appearance}\n"
        f"Предыстория: {chat.background}"
    )

    full_prompt = (
        f"Ты мастер ролевой игры. Персонаж игрока:\n{character_info}\n"
        f"Игрок пишет: {user_message}"
    )

    db.close()
    print("Отправляемый prompt для ИИ:\n", full_prompt)

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
        "messages": [{"role": "user", "content": full_prompt}],
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

@app.route('/characters', methods=['POST'])
def create_character():
    data = request.get_json()

    # Простая проверка на наличие обязательных полей
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400

    character = save_character(data)
    if character:
        return jsonify({"id": character.id, "name": character.name, "created_at": character.created_at.isoformat()}), 201
    else:
        return jsonify({'error': 'Failed to create character'}), 500

@app.route('/characters', methods=['GET'])
def get_characters():
    characters = get_all_characters()
    return jsonify([{"id": character.id, "name": character.name, "created_at": character.created_at.isoformat()} for character in characters])

def get_character_by_id(character_id):
    db = SessionLocal()
    try:
        character = db.query(Character).filter(Character.id == character_id, Character.deleted == False).first()
        return character
    except Exception as e:
        print(f"Ошибка получения персонажа: {e}")
        return None
    finally:
        db.close()

@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = get_character_by_id(character_id)
    if not character:
        return jsonify({'error': 'Персонаж не найден'}), 404  # Ошибка 404, если персонаж не найден
    
    # Если персонаж найден, возвращаем его данные
    return jsonify({
        'id': character.id,
        'name': character.name,
        'character_class': character.character_class,
        'race': character.race,
        'level': character.level,
        'strength': character.strength,
        'dexterity': character.dexterity,
        'constitution': character.constitution,
        'intelligence': character.intelligence,
        'wisdom': character.wisdom,
        'charisma': character.charisma,
        'appearance': character.appearance,
        'background': character.background
    })        

@app.route('/characters/<int:character_id>/delete', methods=['POST'])
def delete_character(character_id):
    db = SessionLocal()
    try:
        character = db.query(Character).filter(Character.id == character_id).first()
        if character:
            character.deleted = True
            db.commit()
            return jsonify({'message': f'Персонаж {character_id} успешно удален.'}), 200
        else:
            return jsonify({'error': 'Персонаж не найден.'}), 404
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Ошибка удаления персонажа: {e}'}), 500
    finally:
        db.close()

def generate_character_data(partial_data):
    # Формируем промпт
    prompt = "На основе указанных данных заполни недостающие поля персонажа DnD. Если на основе данных их заполнить не получается, то придумай любые данные сам. Верни результат в формате JSON со следующими ключами: " \
             "strength, dexterity, constitution, intelligence, wisdom, charisma, appearance, background.\n"
    for key, value in partial_data.items():
        if value:
            prompt += f"{key.capitalize()}: {value}\n"

    # Получение токена
    access_token = get_access_token()
    if not access_token:
        return None, 'Ошибка авторизации.'

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    payload = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": prompt}],
        "n": 1,
        "stream": False,
        "max_tokens": 512,
        "repetition_penalty": 1,
        "update_interval": 0
    }

    response = requests.post(GIGACHAT_API_URL, headers=headers, json=payload, verify=False)

    if response.status_code == 200:
        content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        print("Полный ответ модели:\n", content)

        # Попытка найти JSON-блок
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if match:
            try:
                parsed_json = json.loads(match.group(1))
                print("Извлечённый JSON:\n", parsed_json)
                return parsed_json, None
            except json.JSONDecodeError as e:
                return None, f"Ошибка декодирования JSON: {e}"
        else:
            return None, "JSON не найден в ответе модели."
    else:
        return None, f"Ошибка: {response.status_code} - {response.text}"


@app.route('/characters/generate', methods=['POST'])
def generate_character():
    data = request.get_json()

    response_text, error = generate_character_data(data)
    if error:
        return jsonify({'error': error}), 500

    try:
        generated = response_text
    except json.JSONDecodeError:
        return jsonify({'error': 'Ответ от модели не является корректным JSON.'}), 500

    return jsonify(generated), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
