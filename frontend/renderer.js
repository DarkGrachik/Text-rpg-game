const { ipcRenderer } = require('electron');
let currentChatId = null;

document.addEventListener('DOMContentLoaded', () => {
    const startChatsButton = document.getElementById('chats-button');
    const newChatButton = document.getElementById('new-chat-button');
    const backToMenuButton = document.getElementById('menu-button');
    const backButton = document.getElementById('back-button');

    if (startChatsButton) {
        startChatsButton.addEventListener('click', () => {
            ipcRenderer.send('navigate-to-chats');
        });
    }

    if (backToMenuButton) {
        backToMenuButton.addEventListener('click', () => {
            ipcRenderer.send('navigate-to-menu');
        });
    }

    if (newChatButton) {
        newChatButton.addEventListener('click', () => {
            ipcRenderer.send('navigate-to-new-chat'); // Вызовем функцию создания чата
        });
    }

    if (backButton) {
        backButton.addEventListener('click', () => {
            ipcRenderer.send('navigate-back'); // Возврат на предыдущую страницу
        });
    }

    const createChatButton = document.getElementById('create-chat-button');
    if (createChatButton) {
        createChatButton.addEventListener('click', () => {
            const title = document.getElementById('new-chat-title').value.trim();
            if (title) {
                createNewChat(title); // Создаем чат
            } else {
                alert("Введите название чата.");
            }
        });
    }
});

// Функция для загрузки списка чатов
function loadChats() {
    fetch('http://localhost:5000/chats')  // Обновите URL на свой серверный путь для получения чатов
        .then(response => response.json())
        .then(data => {
            const chatList = document.getElementById('chat-list');
            chatList.innerHTML = ''; // Очистить текущий список чатов

            data.forEach(chat => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `<button class="button" onclick="openChat(${chat.id})">${chat.title}</button> <button style="background-color: red" onclick="deleteChat(${chat.id})">del</button>`;
                console.log('Кнопка добавлена для чата:', chat.id, chat.title);
                chatList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error('Ошибка при загрузке чатов:', error);
        });
}

// Загрузить чаты при открытии страницы
if (document.getElementById('chat-list')) {
    loadChats();
}

// Открытие чата по нажатию на его кнопку
function openChat(chatId) {
    console.log('openChat вызван с chatId:', chatId);
    currentChatId = chatId;
    localStorage.setItem('currentChatId', chatId);
    ipcRenderer.send('navigate-to-chat', chatId);
}

// document.addEventListener('DOMContentLoaded', () => {
//     const startChatButton = document.getElementById('chat-button');

//     if (startChatButton) {
//         startChatButton.addEventListener('click', () => {
//             ipcRenderer.send('navigate-to-chat');
//         });
//     }
// });

function createNewChat(title) {
    fetch('http://localhost:5000/chats', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: title })
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text); });
        }
        return response.json();
    })
    .then(data => {
        if (data.id) {
            alert("Чат создан успешно!");
            window.location.href = 'chats.html'; // Переход к списку чатов
        } else {
            alert("Ошибка при создании чата.");
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert("Ошибка при создании чата.");
    });
}


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
    const chatId = localStorage.getItem('currentChatId');
    console.log('вызван с chatId:', chatId);
    // if (!currentChatId) {
    //     console.error('Chat ID не найден!');
    //     return; // Если нет chat_id, не отправляем сообщение
    // }

    addMessage('Вы', input, true); // Отображаем сообщение пользователя сразу

    // Отправка сообщения на бекенд
    fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: input, chat_id: chatId })
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

document.addEventListener('DOMContentLoaded', () => {
    const chatId = localStorage.getItem('currentChatId'); // Получаем chatId из localStorage
    if (chatId) {
        loadMessages(chatId); // Загружаем сообщения для выбранного чата
    } else {
        console.error('Chat ID не найден! Невозможно загрузить сообщения.');
    }
});

    // Функция для загрузки всех сообщений
    function loadMessages(chatId) {
        fetch(`http://localhost:5000/messages/${chatId}`)  // Добавлен chat_id в URL
            .then(response => response.json())
            .then(data => {
                const chatBox = document.getElementById('chat-box');
                chatBox.innerHTML = ''; // Очистить чат перед загрузкой
    
                // Если есть данные, отображаем сообщения
                if (data.length > 0) {
                    data.forEach(message => {
                        const isUser = message.sender === 'user';
                        addMessage(isUser ? 'Вы' : 'ИИ', message.content, isUser);
                    });
                } else {
                    chatBox.innerHTML = 'Сообщений нет.';
                }
            })
            .catch(error => {
                console.error('Ошибка при загрузке сообщений:', error);
            });
    }

    function deleteChat(chatId) {
        if (confirm('Вы уверены, что хотите удалить этот чат?')) {
            fetch(`http://localhost:5000/chats/${chatId}/delete`, { // URL для удаления чата
                method: 'POST'
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => { throw new Error(text); });
                }
                return response.json();
            })
            .then(() => {
                alert('Чат успешно удалён!');
                loadChats(); // Обновляем список чатов
            })
            .catch(error => {
                console.error('Ошибка при удалении чата:', error);
                alert('Не удалось удалить чат. Попробуйте снова.');
            });
        }
    }

// Загрузка сообщений при открытии чата
// document.addEventListener('DOMContentLoaded', () => {
//     loadMessages();
// });


