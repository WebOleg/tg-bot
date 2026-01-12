from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from datetime import datetime, timedelta

from database import get_transactions_for_forecast
from ml.linear_model import forecast_series
from utils.charts import build_forecast_chart

router = Router()


class ForecastState(StatesGroup):
    days = State()


@router.message(lambda m: m.text == "🔮 Прогноз")
async def start(message: Message, state: FSMContext):
    await message.answer("Введіть кількість днів для прогнозу:")
    await state.set_state(ForecastState.days)


@router.message(ForecastState.days)
async def make_forecast(message: Message, state: FSMContext):
    try:
        days = int(message.text)
        if days <= 0 or days > 365:
            await message.answer("❌ Будь ласка, введіть число від 1 до 365")
            return
    except ValueError:
        await message.answer("❌ Будь ласка, введіть коректне число")
        return

    # Получаем транзакции из БД (даты уже в формате YYYY-MM-DD)
    rows = get_transactions_for_forecast(message.from_user.id)
    if not rows:
        await message.answer("❌ Недостатньо даних для прогнозу. Спочатку додайте транзакції.")
        await state.clear()
        return

    expenses = []
    incomes = []

    # Разделяем на доходы и расходы
    for date_db, amount, t_type in rows:
        if t_type == "expense":
            expenses.append(amount)
            incomes.append(0)
        else:
            incomes.append(amount)
            expenses.append(0)

    # Если недостаточно данных для прогноза
    if len(expenses) < 2 and len(incomes) < 2:
        await message.answer("❌ Недостатньо даних для прогнозу. Потрібно хоча б 2 транзакції.")
        await state.clear()
        return

    # Прогнозируем
    expense_pred = forecast_series(expenses, days)
    income_pred = forecast_series(incomes, days)

    balance_pred = income_pred - expense_pred
    total_balance = balance_pred.sum()

    # Рассчитываем среднемесячный доход
    total_income = sum(incomes)
    if total_income > 0:
        avg_month_income = total_income / max(1, len(incomes)) * 30
    else:
        avg_month_income = 0

    # Определяем статус
    if avg_month_income == 0:
        status = "⚪ Немає даних про доходи"
        advice = "Додайте дані про доходи для точного прогнозу"
    elif total_balance < -2 * avg_month_income:
        status = "🔴 КРИТИЧНО"
        advice = "Терміново скоротити витрати або збільшити дохід"
    elif total_balance < -avg_month_income:
        status = "🟠 Суворе попередження"
        advice = "Фінансова ситуація погіршується"
    elif total_balance < 0:
        status = "🟡 Попередження"
        advice = "Стежте за витратами"
    elif total_balance < 2 * avg_month_income:
        status = "🟢 Стабільно"
        advice = "Фінансова ситуація під контролем"
    else:
        status = "🟢 Відмінно"
        advice = "Хороший запас фінансової міцності"

    # Формируем текст с информацией о последних транзакциях
    last_transactions = rows[-5:] if len(rows) >= 5 else rows
    last_dates_text = "\n".join([
        f"{datetime.strptime(date_db, '%Y-%m-%d').strftime('%d.%m.%Y')}: {amount:.2f} ({'витрата' if t_type == 'expense' else 'дохід'})"
        for date_db, amount, t_type in last_transactions
    ])

    text = (
        f"📊 Прогноз на {days} днів\n\n"
        f"📈 Останні транзакції:\n{last_dates_text}\n\n"
        f"💰 Середній місячний дохід: {avg_month_income:.2f}\n"
        f"⚖️ Прогнозований баланс: {total_balance:.2f}\n\n"
        f"{status}\n"
        f"💡 {advice}"
    )

    # Строим график
    try:
        chart_path = build_forecast_chart(
            expense_pred,
            income_pred,
            balance_pred
        )
        
        await message.answer(text)
        await message.answer_photo(FSInputFile(chart_path))
        
    except Exception as e:
        await message.answer(f"{text}\n\n⚠️ Не вдалося побудувати графік: {str(e)}")
    
    await state.clear()
