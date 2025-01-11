// main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let win;

function createWindow() {
    win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'renderer.js'),
            contextIsolation: false,
            nodeIntegration: true,
        }
    });

    loadPage('menu.html'); // Загрузка меню при запуске приложения
}

function loadPage(page) {
    win.loadFile(path.join(__dirname, 'pages', page));
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Обработка сообщения от рендерера для переключения страниц
ipcMain.on('navigate-to-chats', () => {
    loadPage('chats.html');
});

ipcMain.on('navigate-to-menu', () => {
    loadPage('menu.html');
});

ipcMain.on('navigate-to-chat', () => {
    loadPage('chat_app.html');
});

ipcMain.on('navigate-to-new-chat', () => {
    loadPage('new_chat.html'); // Переход на страницу нового чата
});

ipcMain.on('navigate-back', () => {
    loadPage('chats.html'); // Переход на главную страницу
});


