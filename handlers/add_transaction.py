from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import datetime

from database import add_transaction, get_categories_by_type
from keyboards import categories_kb, skip_kb, main_menu

router = Router()

class AddTransaction(StatesGroup):
    amount = State()
    date = State()
    category = State()
    note = State()
    t_type = State()

# --- Початок ---
@router.message(F.text.in_(["➕ Додати платіж", "💰 Додати дохід"]))
async def start(message: Message, state: FSMContext):
    t_type = "expense" if "платіж" in message.text else "income"
    await state.update_data(t_type=t_type)
    await message.answer("Введіть суму:")
    await state.set_state(AddTransaction.amount)

# --- Сума ---
@router.message(AddTransaction.amount)
async def get_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введіть число, наприклад: 123.45")
        return

    await state.update_data(amount=amount)
    await message.answer("Введіть дату (ДД.ММ.РРРР) або напишіть 'сьогодні':")
    await state.set_state(AddTransaction.date)

# --- Дата ---
@router.message(AddTransaction.date)
async def get_date(message: Message, state: FSMContext):
    user_date = message.text.strip().lower()
    
    try:
        if user_date == "сьогодні":
            date_obj = datetime.now()
        elif "." in user_date:  # Формат ДД.ММ.РРРР
            date_obj = datetime.strptime(user_date, "%d.%m.%Y")
        elif "-" in user_date:  # Формат РРРР-ММ-ДД (на всякий случай)
            date_obj = datetime.strptime(user_date, "%Y-%m-%d")
        else:
            await message.answer("❌ Невірний формат дати. Використовуйте ДД.ММ.РРРР (наприклад, 05.01.2026)")
            return
        
        # Конвертируем в YYYY-MM-DD для хранения в БД
        db_date = date_obj.strftime("%Y-%m-%d")
        # Сохраняем и для отображения пользователю
        display_date = date_obj.strftime("%d.%m.%Y")
        
    except ValueError:
        await message.answer("❌ Невірна дата. Використовуйте формат ДД.ММ.РРРР (наприклад, 05.01.2026)")
        return
    
    await state.update_data(date=db_date, display_date=display_date)

    data = await state.get_data()
    categories = get_categories_by_type(data["t_type"])

    await message.answer(
        f"Дата: {display_date}\nОберіть категорію:",
        reply_markup=categories_kb(categories)
    )
    await state.set_state(AddTransaction.category)

# --- Категорія ---
@router.callback_query(AddTransaction.category)
async def get_category(call: CallbackQuery, state: FSMContext):
    await state.update_data(category_id=int(call.data))
    
    data = await state.get_data()
    display_date = data.get("display_date", "")

    await call.message.answer(
        f"Дата: {display_date}\nВведіть примітку або натисніть «Пропустити»:",
        reply_markup=skip_kb
    )
    await state.set_state(AddTransaction.note)

# --- Примітка + ЗБЕРЕЖЕННЯ ---
@router.message(AddTransaction.note)
async def get_note(message: Message, state: FSMContext):
    note = None if message.text == "⏭ Пропустити" else message.text

    data = await state.get_data()
    display_date = data.get("display_date", "")

    add_transaction(
        user_id=message.from_user.id,
        amount=data["amount"],
        date=data["date"],  # В формате YYYY-MM-DD
        category_id=data["category_id"],
        t_type=data["t_type"],
        note=note
    )

    await message.answer(f"✅ Запис збережено\nДата: {display_date}", reply_markup=main_menu)
    await state.clear()
