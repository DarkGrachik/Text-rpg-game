const { ipcRenderer } = require('electron');
let currentCharacterId = null;



document.addEventListener('DOMContentLoaded', () => {
    const charactersButton = document.getElementById('characters-button');
    const newCharacterButton = document.getElementById('new-character-button');
    const backToMenuButton = document.getElementById('menu-button');
    const backToCharactersButton = document.getElementById('back-to-characters');

    if (charactersButton) {
        charactersButton.addEventListener('click', () => {
            ipcRenderer.send('navigate-to-characters');
        });
    }

    if (backToMenuButton) {
        backToMenuButton.addEventListener('click', () => {
            ipcRenderer.send('navigate-to-menu');
        });
    }

    if (newCharacterButton) {
        newCharacterButton.addEventListener('click', () => {
            ipcRenderer.send('navigate-to-new-character'); // Вызовем функцию создания чата
        });
    }

    if (backToCharactersButton) {
        backToCharactersButton.addEventListener('click', () => {
            ipcRenderer.send('navigate-to-characters'); // Возврат на предыдущую страницу
        });
    }

    const createCharacterButton = document.getElementById('create-character-button');
    if (createCharacterButton) {
        createCharacterButton.addEventListener('click', () => {
            const characterData = {
                name: document.getElementById('character-name').value.trim(),
                character_class: document.getElementById('character-class').value.trim(),
                race: document.getElementById('character-race').value.trim(),
                strength: parseInt(document.getElementById('strength').value),
                dexterity: parseInt(document.getElementById('dexterity').value),
                constitution: parseInt(document.getElementById('constitution').value),
                intelligence: parseInt(document.getElementById('intelligence').value),
                wisdom: parseInt(document.getElementById('wisdom').value),
                charisma: parseInt(document.getElementById('charisma').value),
                level: parseInt(document.getElementById('level').value),
                appearance: document.getElementById('appearance').value.trim(),
                background: document.getElementById('background').value.trim(),
            };
    
            if (!characterData.name) {
                alert("Введите имя персонажа.");
                return;
            }
    
            // Добавь здесь проверки других обязательных полей при необходимости
    
            createNewCharacter(characterData);
        });
    }

    const generateCharacterButton = document.getElementById('generate-character-button');
    if (generateCharacterButton) {
        generateCharacterButton.addEventListener('click', () => {
            const partialData = {
                name: document.getElementById('character-name').value.trim(),
                character_class: document.getElementById('character-class').value.trim(),
                race: document.getElementById('character-race').value.trim(),
                appearance: document.getElementById('appearance').value.trim(),
                background: document.getElementById('background').value.trim()
            };
    
            fetch('http://localhost:5000/characters/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(partialData)
            })
            .then(response => response.json())
            .then(data => {
                const shouldUpdate = value => value === '' || value === '0' || value === '0.0';
    
                const fields = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma', 'appearance', 'background'];
                fields.forEach(field => {
                    const input = document.getElementById(field);
                    if (input && shouldUpdate(input.value)) {
                        input.value = data[field];
                    }
                });
            })
            .catch(error => {
                console.error('Ошибка при генерации персонажа:', error);
                alert("Не удалось сгенерировать персонажа.");
            });
        });
    }
});

// Функция для загрузки списка чатов
function loadCharacters() {
    fetch('http://localhost:5000/characters')  // Обновите URL на свой серверный путь для получения чатов
        .then(response => response.json())
        .then(data => {
            const characterList = document.getElementById('character-list');
            characterList.innerHTML = ''; // Очистить текущий список чатов

            data.forEach(character => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `<button class="button" onclick="openCharacter(${character.id})">${character.name}</button> <button style="background-color: red" onclick="deleteCharacter(${character.id})">del</button>`;
                console.log('Кнопка добавлена для персонажа:', character.id, character.name);
                characterList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error('Ошибка при загрузке персонажей:', error);
        });
}

// Загрузить чаты при открытии страницы
if (document.getElementById('character-list')) {
    loadCharacters();
}

// Открытие чата по нажатию на его кнопку
function openCharacter(characterId) {
    console.log('openCharacter вызван с characterId:', characterId);
    currentCharacterId = characterId;
    localStorage.setItem('currentCharacterId', characterId);
    ipcRenderer.send('navigate-to-character', characterId);
}

// document.addEventListener('DOMContentLoaded', () => {
//     const startChatButton = document.getElementById('chat-button');

//     if (startChatButton) {
//         startChatButton.addEventListener('click', () => {
//             ipcRenderer.send('navigate-to-chat');
//         });
//     }
// });

function createNewCharacter(characterData) {
    fetch('http://localhost:5000/characters', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(characterData)
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text); });
        }
        return response.json();
    })
    .then(data => {
        if (data.id) {
            alert("Персонаж создан успешно!");
            window.location.href = 'characters.html'; // Переход к списку персонажей
        } else {
            alert("Ошибка при создании персонажа.");
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert("Ошибка при создании персонажа: " + error.message);
    });
}


document.addEventListener('DOMContentLoaded', () => {
    const backToMenuButton = document.getElementById('menu-button');

    if (backToMenuButton) {
        backToMenuButton.addEventListener('click', () => {
            ipcRenderer.send('navigate-to-menu');
        });currentCharacterId
    }
});


document.addEventListener("DOMContentLoaded", () => {
    const infoContainer = document.getElementById("character-info");
    if (!infoContainer) return;

    const characterId = localStorage.getItem('currentCharacterId');

    if (!characterId) {
        document.getElementById("character-info").textContent = "ID персонажа не указан.";
        return;
    }

    fetch(`http://localhost:5000/characters/${characterId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById("character-info").textContent = data.error;
                return;
            }

            const container = document.getElementById("character-info");
            const fieldsToDisplay = [
                { key: "name", label: "Имя" },
                { key: "character_class", label: "Класс" },
                { key: "race", label: "Раса" },
                { key: "level", label: "Уровень" },
                { key: "strength", label: "Сила" },
                { key: "dexterity", label: "Ловкость" },
                { key: "constitution", label: "Телосложение" },
                { key: "intelligence", label: "Интеллект" },
                { key: "wisdom", label: "Мудрость" },
                { key: "charisma", label: "Харизма" },
                { key: "appearance", label: "Внешность" },
                { key: "background", label: "Предыстория" },
            ];

            fieldsToDisplay.forEach(field => {
                const fieldWrapper = document.createElement("div");
                fieldWrapper.className = "character-field";

                const label = document.createElement("div");
                label.className = "character-label";
                label.textContent = field.label;

                const value = document.createElement("div");
                value.className = "character-value";
                value.textContent = data[field.key] ?? "—";

                fieldWrapper.appendChild(label);
                fieldWrapper.appendChild(value);
                container.appendChild(fieldWrapper);
            });
        })
        .catch(err => {
            document.getElementById("character-info").textContent = "Ошибка при загрузке данных.";
            console.error(err);
        });

    document.getElementById("back-to-characters").addEventListener("click", () => {
        ipcRenderer.send('navigate-to-characters');
    });
});

function deleteCharacter(characterId) {
    if (confirm('Вы уверены, что хотите удалить этого персонажа?')) {
        fetch(`http://localhost:5000/characters/${characterId}/delete`, { // URL для удаления персонажа
            method: 'POST'
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text); });
            }
            return response.json();
        })
        .then(() => {
            alert('Персонаж успешно удалён!');
            loadCharacters(); // Обновляем список персонажей
        })
        .catch(error => {
            console.error('Ошибка при удалении персонажа:', error);
            alert('Не удалось удалить персонажа. Попробуйте снова.');
        });
    }
}
