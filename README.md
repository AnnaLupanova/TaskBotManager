# TaskManagerBot
**Общее описание задачи**\
Задача — разработать Telegram-бот для управления задачами с поддержкой пользователей, регистрацией, функциональностью добавления, просмотра, завершения и удаления задач.

**Технологии**
* Pyrogram: Используется для взаимодействия с Telegram API.
* Asyncio: Для асинхронного выполнения задач.
* Asyncpg: Для работы с PostgreSQL.

**Основные компоненты системы:**

* Telegram Bot: Основной интерфейс взаимодействия с пользователем. Реализует обработку команд, сообщений и обратных вызовов.
* Database (PostgreSQL): Хранилище данных о пользователях и их задачах.
* AsyncPG: Библиотека для работы с PostgreSQL, обеспечивает асинхронное взаимодействие с базой данных.


**Функциональность**

* Регистрация пользователя.
* Создание задач.
* Просмотр задач с пагинацией.
* Завершение и удаление задач.


**Диаграмма компонентов и взаимодействий**

[User] --> [Telegram Bot] --> [Logic] --> [Database]

* User: Отправляет команды через Telegram.
* Telegram Bot: Использует библиотеку pyrogram для обработки событий и отправки сообщений.
* Logic: Взаимодействует с базой данных через классы и функции, обрабатывает команды пользователя.
* Database: Хранит данные о пользователях и задачах.


**Пример использования бота**

* Пример 1: Регистрация. Пользователь отправляет /start. Бот запрашивает ввод имени. Далее запрашив теалогин.
После ввода уникального логина пользователь регистрируется в базе.

* Пример 2: Добавление задачи. 
Пользователь нажимает на кнопку 📝 Создать задачу.
Бот запрашивает название задачи.
После ввода названия бот запрашивает описание.
Задача сохраняется, бот отправляет подтверждение.

* Пример 3: Просмотр задач
Пользователь нажимает на кнопку 📋 Мои задачи.
Бот возвращает список задач. На каждую задачу можно перейти и с помощью кнопок 
пометить задачу как выполненную или удалить.

* Пример 4: Завершение задачи
Пользователь нажимает кнопку "Завершить". Задача помечается как выполненная.

**Структура базы данных**

В базе данных используются две таблицы: users и tasks.

Таблица users хранит информацию о пользователях, включая их идентификатор Telegram, имя, логин, и имя пользователя.
Таблица tasks хранит информацию о задачах, привязанных к пользователям.

```
CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNIQUE NOT NULL PRIMARY KEY,  -- Уникальный идентификатор Telegram
    name TEXT NOT NULL,                     -- Имя пользователя
    login TEXT NOT NULL,                    -- Логин пользователя
    username TEXT NOT NULL,                 -- Имя пользователя в Telegram
    CONSTRAINT login_unique UNIQUE (login) -- Ограничение на уникальность логина
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,                 -- Уникальный идентификатор задачи
    user_id BIGINT NOT NULL,               -- Telegram ID пользователя
    title TEXT NOT NULL,                   -- Название задачи
    description TEXT,                      -- Описание задачи
    is_completed BOOLEAN DEFAULT FALSE,    -- Статус выполнения (по умолчанию "не выполнена")
    FOREIGN KEY (user_id) REFERENCES users (id) -- Связь с таблицей users
);
```
**Разворачивание проекта:**
* Клонируйте репозиторий git clone <url_git_repo>
* Перейдите в директорию cd TaskBotManager
* Внесите правки в docker-compose.yml:
  *  Для контейнера telegram_bot пропишите в пункте environment реквизиты доступа для ТГ API (API_ID,API_HASH,BOT_TOKEN)

* Запустите проект с помощью команды  docker-compose up -d