from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import main_menu

router = Router()

@router.message(CommandStart())
@router.message(Command("menu"))
@router.message(lambda m: m.text and m.text.lower() in ["меню", "menu"])
async def show_menu(message: Message, state: FSMContext = None):
    """Показати главное меню (для /start, /menu и текста 'меню')"""
    
    
    if state:
        await state.clear()
    
    await message.answer(
        "👋 Вітаю! Бот для ведення фінансів готовий до роботи.\n"
        "📱 Використовуйте меню нижче:",
        reply_markup=main_menu
    )


@router.message(lambda m: m.text == "🏠 Головне меню")
async def back_to_menu(message: Message, state: FSMContext):
    """В главное меню из любого состояния"""
    await state.clear()
    await show_menu(message)