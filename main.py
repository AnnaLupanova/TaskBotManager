from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from states import FSM, States
from keyboards import task_keyboard, main_menu
from database import Database
from typing import List, Dict, Optional, Union
from pyrogram.types import CallbackQuery
from os import getenv

DATABASE_URL = getenv("DATABASE_URL")
app = Client("task_manage_bot", api_id=getenv("API_ID", None), api_hash=getenv("API_HASH", None), bot_token=getenv("BOT_TOKEN", None))
db = Database(DATABASE_URL)
user_states = FSM()


@app.on_message(filters.command("start") | filters.regex("🏠 Главное меню"))
async def start(client: Client, message: Message) -> None:
    """Обработчик команды /start или кнопки 'Главное меню'."""
    user_id = message.from_user.id
    user = await db.get_user_by_telegram_id(user_id)
    user_states.clear_state(user_id)
    if not user:
        await message.reply("Привет! Пожалуйста, введите своё имя, чтобы зарегистрироваться.")
        user_states.set_state(user_id, States.REGISTERING)
    else:
        await message.reply("Добро пожаловать! Вы можете управлять своими задачами.", reply_markup=main_menu())


@app.on_message(filters.regex("📝 Создать задачу"))
async def create_task(client: Client, message: Message) -> None:
    """Обработчик создания новой задачи."""
    user_id = message.from_user.id
    user_states.set_state(user_id, States.CREATE_TASK_TITLE)
    await message.reply("Введите название задачи:")


@app.on_message(filters.regex("📋 Мои задачи"))
async def view_tasks(client: Client, message: Message) -> None:
    """Обработчик отображения списка задач."""
    user_id = message.from_user.id
    tasks = await db.get_tasks(user_id)
    if not tasks:
        await message.reply("У вас нет задач.", reply_markup=main_menu())
    else:
        await send_tasks_with_pagination(message, tasks, 0)


async def send_tasks_with_pagination(message: Union[Message, CallbackQuery], tasks: List[Dict], page: int, need_edit: bool = False) -> None:
    """Отправляет список задач с кнопками пагинации."""
    ITEMS_PER_PAGE = 4
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    task_buttons = [
        [InlineKeyboardButton(f"{task['title']} {'✔' if task['is_completed'] else ''}",
                              callback_data=f"task_{task['id']}")]
        for task in tasks[start:end]
    ]
    navigation_buttons = []
    if start > 0:
        navigation_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"tasks_page_{page - 1}"))
    if end < len(tasks):
        navigation_buttons.append(InlineKeyboardButton("➡️ Вперёд", callback_data=f"tasks_page_{page + 1}"))
    task_buttons.append(navigation_buttons)
    keyboard = InlineKeyboardMarkup(task_buttons)

    if need_edit:
        await message.edit_text("Ваши задачи:", reply_markup=keyboard)
    else:
        await message.reply("Ваши задачи:", reply_markup=keyboard)


@app.on_callback_query(filters.regex(r"^tasks_page_"))
async def handle_task_pagination(client: Client, callback_query: CallbackQuery) -> None:
    """Обработчик переключения страниц задач."""
    page = int(callback_query.data.split("_")[-1])
    user_id = callback_query.from_user.id
    tasks = await db.get_tasks(user_id)
    if tasks:
        await send_tasks_with_pagination(callback_query.message, tasks, page, need_edit=True)


@app.on_callback_query(filters.regex(r"^task_"))
async def manage_task(client: Client, callback_query: CallbackQuery) -> None:
    """Обработчик конкретной задачи."""
    task_id = int(callback_query.data.split("_")[1])
    task = await db.get_task_by_id(task_id)
    if task:
        await callback_query.message.edit_text(
            f"Задача: {task['title']}\nОписание: {task['description']}",
            reply_markup=task_keyboard(task_id, task['is_completed'])
        )


@app.on_callback_query()
async def handle_callbacks(client: Client, callback_query: CallbackQuery) -> None:
    """Обработчик взаимодействия с задачами."""
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data.startswith("complete_"):
        task_id = int(data.split("_")[1])
        await db.complete_task(task_id)
        await callback_query.message.edit_text("Задача завершена.")
        new_message = callback_query.message
        new_message.from_user = callback_query.from_user
        await view_tasks(client, new_message)
    elif data.startswith("delete_"):
        task_id = int(data.split("_")[1])
        await db.delete_task(task_id)
        new_message = callback_query.message
        new_message.from_user = callback_query.from_user
        await callback_query.message.edit_text("Задача удалена!")
        await view_tasks(client, new_message)
    elif data == "back_to_tasks":
        tasks = await db.get_tasks(user_id)
        await send_tasks_with_pagination(callback_query.message, tasks, 0, need_edit=True)


@app.on_message(filters.text)
async def handle_text(client: Client, message: Message) -> None:
    """Обработчик текстовых сообщений для работы FSM."""
    user_id = message.from_user.id
    state = user_states.get_state(user_id)
    user_data = user_states.get_data(user_id)

    if state == States.REGISTERING:
        if 'name' not in user_data:
            user_states.set_data(user_id, {'name': message.text.strip()})
            await message.reply("Теперь введите уникальный логин:")
        else:
            login = message.text.strip()
            if await db.check_exists_user(login):
                await message.reply("Логин уже используется, попробуйте другой.")
            else:
                name = user_states.get_data(user_id)['name']
                await db.add_user(user_id, name, login, message.from_user.username or "")
                await message.reply("Вы успешно зарегистрированы!", reply_markup=main_menu())
                user_states.clear_data(user_id)
                user_states.set_state(user_id, States.MAIN_MENU)
    elif state == States.CREATE_TASK_TITLE:
        user_states.set_data(user_id, {'task_title': message.text.strip()})
        user_states.set_state(user_id, States.CREATE_TASK_DESCRIPTION)
        await message.reply("Введите описание задачи:")
    elif state == States.CREATE_TASK_DESCRIPTION:
        task_title = user_states.get_data(user_id).get('task_title')
        task_description = message.text.strip()
        await db.add_task(user_id, task_title, task_description)
        await message.reply("Задача успешно создана!", reply_markup=main_menu())
        user_states.clear_data(user_id)
        user_states.set_state(user_id, States.MAIN_MENU)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(db.init_pool())
    app.run()
