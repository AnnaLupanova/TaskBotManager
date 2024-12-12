from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def task_keyboard(task_id: int, is_complete: bool) -> InlineKeyboardMarkup:
    if is_complete:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Удалить", callback_data=f"delete_{task_id}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_tasks")]
        ])

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Завершить", callback_data=f"complete_{task_id}"),
         InlineKeyboardButton("❌ Удалить", callback_data=f"delete_{task_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_tasks")]
    ])


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        [KeyboardButton("📝 Создать задачу"), KeyboardButton("📋 Мои задачи")],
        [KeyboardButton("🏠 Главное меню")]
    ], resize_keyboard=True)
