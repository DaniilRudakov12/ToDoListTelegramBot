
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Показать список событий")],
        [KeyboardButton(text="➕ Добавить событие")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню:"
)

status_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Не начато ❌")],
        [KeyboardButton(text="В процессе ⏳")],
        [KeyboardButton(text="Выполнено ✅")],
        [KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню:")

tasks_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅ Назад")],
        [KeyboardButton(text="➕ Добавить событие")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню:"
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню:"
)
