from flask import Flask, request, jsonify
import requests

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

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

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
        return jsonify({'response': ai_response})
    else:
        return jsonify({'response': f"Ошибка: {response.status_code} - {response.text}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
