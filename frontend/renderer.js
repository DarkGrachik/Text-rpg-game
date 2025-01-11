const { ipcRenderer } = require('electron');

document.addEventListener('DOMContentLoaded', () => {
    const startChatButton = document.getElementById('chat-button');

    if (startChatButton) {
        startChatButton.addEventListener('click', () => {
            ipcRenderer.send('navigate-to-chat');
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const backToMenuButton = document.getElementById('menu-button');

    if (backToMenuButton) {
        backToMenuButton.addEventListener('click', () => {
            ipcRenderer.send('navigate-to-menu');
        });
    }
});

// Функция для добавления сообщения в чат
function addMessage(sender, message, isUser) {
    const chat = document.getElementById('chat-box');
    const messageElement = document.createElement('p');
    messageElement.innerHTML = `<b>${sender}:</b> ${message}`;
    messageElement.className = isUser ? 'user' : 'ai';
    chat.appendChild(messageElement);
    chat.scrollTop = chat.scrollHeight; // Прокрутка чата к последнему сообщению
}

// Отправка сообщения по нажатию на кнопку "Отправить"
document.getElementById('send-button').addEventListener('click', () => {
    sendMessage();
});

// Отправка сообщения по нажатию клавиши Enter
document.getElementById('message-input').addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) { // Проверка на клавишу Enter и игнорирование Shift
        event.preventDefault(); // Предотвращение вставки новой строки
        sendMessage();
    }
});

function sendMessage() {
    const input = document.getElementById('message-input').value;
    if (input.trim() === '') return; // Игнорировать пустые сообщения

    addMessage('Вы', input, true); // Отображаем сообщение пользователя сразу

    // Отправка сообщения на бекенд
    fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: input })
    })
    .then(response => response.json())
    .then(data => {
        const aiResponse = data.response || "Нет ответа от ИИ.";
        addMessage('ИИ', aiResponse, false); // Отображаем ответ от ИИ
    })
    .catch(error => {
        console.error('Ошибка:', error);
        addMessage('ИИ', 'Ошибка при подключении к серверу.', false);
    });

    // Очищаем поле ввода после отправки
    document.getElementById('message-input').value = '';
}
