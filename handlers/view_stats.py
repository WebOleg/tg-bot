from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime

from database import get_expense_by_category, get_transactions
from utils.charts import expense_pie_chart
from aiogram.types import FSInputFile
import os

router = Router()

class Period(StatesGroup):
    date_from = State()
    date_to = State()

@router.message(lambda m: m.text == "📊 Переглянути платежі")
async def start(message: Message, state: FSMContext):
    await message.answer("Введіть початкову дату (ДД.ММ.РРРР):")
    await state.set_state(Period.date_from)

@router.message(Period.date_from)
async def get_from(message: Message, state: FSMContext):
    user_date = message.text.strip()
    try:
        date_obj = datetime.strptime(user_date, "%d.%m.%Y")
        db_date = date_obj.strftime("%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Невірний формат. Використовуйте ДД.ММ.РРРР")
        return
    await state.update_data(date_from=db_date, display_from=user_date)
    await message.answer("Введіть кінцеву дату (ДД.ММ.РРРР):")
    await state.set_state(Period.date_to)

@router.message(Period.date_to)
async def get_to(message: Message, state: FSMContext):
    user_date = message.text.strip()
    try:
        date_obj = datetime.strptime(user_date, "%d.%m.%Y")
        db_date = date_obj.strftime("%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Невірний формат. Використовуйте ДД.ММ.РРРР")
        return
    
    data = await state.get_data()
    rows = get_transactions(message.from_user.id, data["date_from"], db_date)

    if not rows:
        await message.answer(f"Немає даних за період {data['display_from']} - {user_date}")
        await state.clear()
        return

    income_sum = 0.0
    expense_sum = 0.0
    lines = []

    for date_db, category, amount, t_type, note in rows:
        date_display = datetime.strptime(date_db, "%Y-%m-%d").strftime("%d.%m.%Y")
        if t_type == "expense":
            expense_sum += amount
            sign = "−"
        else:
            income_sum += amount
            sign = "+"
        note_text = f" ({note})" if note else ""
        lines.append(f"{date_display} | {category} | {sign}{amount:.2f}{note_text}")

    # РОЗБИВКА НА ЧАСТИНИ (max 4000 символів)
    MAX_LEN = 4000
    chunks = []
    current_chunk = ""
    
    for line in lines:
        if len(current_chunk) + len(line) + 1 > MAX_LEN:
            chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk = current_chunk + "\n" + line if current_chunk else line
    
    if current_chunk:
        chunks.append(current_chunk)
    
    # Відправляємо частини
    for i, chunk in enumerate(chunks):
        await message.answer(f"📄 Частина {i+1}/{len(chunks)}\n\n{chunk}")

    # Підсумок окремим повідомленням
    summary = (
        f"📅 Період: {data['display_from']} - {user_date}\n"
        f"💸 Витрати: {expense_sum:.2f}\n"
        f"💰 Доходи: {income_sum:.2f}\n"
        f"📊 Баланс: {(income_sum - expense_sum):.2f}"
    )
    await message.answer(summary)
    
    # Графік
    chart_data = get_expense_by_category(message.from_user.id, data["date_from"], db_date)
    if chart_data:
        chart_file = expense_pie_chart(chart_data)
        await message.answer_photo(FSInputFile(chart_file))
        os.remove(chart_file)

    await state.clear()
