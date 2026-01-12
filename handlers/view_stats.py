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
        # Конвертируем из ДД.ММ.РРРР в YYYY-MM-DD
        date_obj = datetime.strptime(user_date, "%d.%m.%Y")
        db_date = date_obj.strftime("%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Невірний формат. Використовуйте ДД.ММ.РРРР (наприклад, 01.01.2026)")
        return
    
    await state.update_data(date_from=db_date, display_from=user_date)
    await message.answer("Введіть кінцеву дату (ДД.ММ.РРРР):")
    await state.set_state(Period.date_to)

@router.message(Period.date_to)
async def get_to(message: Message, state: FSMContext):
    user_date = message.text.strip()
    
    try:
        # Конвертируем из ДД.ММ.РРРР в YYYY-MM-DD
        date_obj = datetime.strptime(user_date, "%d.%m.%Y")
        db_date = date_obj.strftime("%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Невірний формат. Використовуйте ДД.ММ.РРРР (наприклад, 31.01.2026)")
        return
    
    data = await state.get_data()
    
    rows = get_transactions(
        message.from_user.id,
        data["date_from"],
        db_date
    )

    if not rows:
        await message.answer(f"Немає даних за період {data['display_from']} - {user_date}")
        await state.clear()
        return

    income_sum = 0.0
    expense_sum = 0.0
    lines = []

    for date_db, category, amount, t_type, note in rows:
        # Конвертируем дату обратно для отображения
        date_display = datetime.strptime(date_db, "%Y-%m-%d").strftime("%d.%m.%Y")
        
        if t_type == "expense":
            expense_sum += amount
            sign = "−"
        else:
            income_sum += amount
            sign = "+"

        note_text = f" ({note})" if note else ""
        lines.append(
            f"{date_display} | {category} | {sign}{amount:.2f}{note_text}"
        )

    text = "\n".join(lines)

    summary = (
        f"\n\n"
        f"📅 Період: {data['display_from']} - {user_date}\n"
        f"💸 Витрати: {expense_sum:.2f}\n"
        f"💰 Доходи: {income_sum:.2f}\n"
        f"📊 Баланс: {(income_sum - expense_sum):.2f}"
    )

    await message.answer(text + summary)
    
    # График (используем даты в формате БД)
    chart_data = get_expense_by_category(
        message.from_user.id,
        data["date_from"],
        db_date
    )

    if chart_data:
        chart_file = expense_pie_chart(chart_data)
        await message.answer_photo(FSInputFile(chart_file))
        os.remove(chart_file)

    await state.clear()
