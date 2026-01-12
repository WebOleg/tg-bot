from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Додати платіж"), KeyboardButton(text="💰 Додати дохід")],
        [KeyboardButton(text="📊 Переглянути платежі")],
        [KeyboardButton(text="🔮 Прогноз"), KeyboardButton(text="🏠 Головне меню")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Оберіть дію..."
)


skip_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏭ Пропустити")],
        [KeyboardButton(text="🏠 Головне меню")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Скасувати")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

def categories_kb(categories):
    """Инлайн-клавиатура с категориями"""
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=str(cat_id))]
        for cat_id, name in categories
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)