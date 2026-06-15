from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from datetime import datetime

from database import get_transactions_for_forecast
from ml.linear_model import forecast_with_metrics
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

    rows = get_transactions_for_forecast(message.from_user.id)
    if not rows:
        await message.answer("❌ Недостатньо даних для прогнозу.")
        await state.clear()
        return

    daily_expenses = {}
    daily_incomes = {}
    
    for date_db, amount, t_type in rows:
        if t_type == "expense":
            daily_expenses[date_db] = daily_expenses.get(date_db, 0) + amount
        else:
            daily_incomes[date_db] = daily_incomes.get(date_db, 0) + amount

    all_dates = sorted(set(daily_expenses.keys()) | set(daily_incomes.keys()))
    
    if len(all_dates) < 2:
        await message.answer("❌ Недостатньо даних. Потрібно хоча б 2 дні з транзакціями.")
        await state.clear()
        return

    expenses_by_day = [daily_expenses.get(d, 0) for d in all_dates]
    incomes_by_day = [daily_incomes.get(d, 0) for d in all_dates]

    total_income = sum(incomes_by_day)
    total_expense = sum(expenses_by_day)
    current_balance = total_income - total_expense
    
    first_date = datetime.strptime(all_dates[0], "%Y-%m-%d")
    last_date = datetime.strptime(all_dates[-1], "%Y-%m-%d")
    days_in_period = (last_date - first_date).days + 1
    
    avg_daily_expense = total_expense / days_in_period if days_in_period > 0 else 0
    avg_daily_income = total_income / days_in_period if days_in_period > 0 else 0
    
    avg_month_income = avg_daily_income * 30
    avg_month_expense = avg_daily_expense * 30
    avg_month_balance = avg_month_income - avg_month_expense

    # === ПРОГНОЗ З МЕТРИКАМИ ===
    expense_result = forecast_with_metrics(expenses_by_day, days)
    income_result = forecast_with_metrics(incomes_by_day, days)
    
    expense_pred = expense_result['prediction']
    income_pred = income_result['prediction']
    
    # Метрики якості моделі
    r2_expense = expense_result['r2']
    r2_income = income_result['r2']
    mae_expense = expense_result['mae']
    mae_income = income_result['mae']
    
    predicted_total_expense = sum(expense_pred)
    predicted_total_income = sum(income_pred)
    predicted_balance = current_balance + (predicted_total_income - predicted_total_expense)

    # === ОЦІНКА ЯКОСТІ МОДЕЛІ ===
    avg_r2 = (r2_expense + r2_income) / 2
    if avg_r2 >= 0.8:
        quality = "🟢 Висока точність"
    elif avg_r2 >= 0.5:
        quality = "🟡 Середня точність"
    elif avg_r2 >= 0.2:
        quality = "🟠 Низька точність"
    else:
        quality = "🔴 Дуже низька (тренд нестабільний)"

    # === RULE-BASED СТАТУС ===
    if avg_month_income == 0:
        status = "⚪ Немає даних про доходи"
        advice = "Додайте дані про доходи для точного прогнозу"
    elif avg_month_balance < -2 * avg_month_income:
        status = "🔴 КРИТИЧНО"
        advice = "Терміново скоротити витрати або збільшити дохід"
    elif avg_month_balance < -avg_month_income:
        status = "🟠 Суворе попередження"
        advice = "Фінансова ситуація погіршується"
    elif avg_month_balance < 0:
        status = "🟡 Попередження"
        advice = "Стежте за витратами"
    elif avg_month_balance < avg_month_income:
        status = "🟢 Стабільно"
        advice = "Фінансова ситуація під контролем"
    else:
        status = "🟢 Відмінно"
        advice = "Хороший запас фінансової міцності"

    text = (
        f"📊 Прогноз на {days} днів (лінійна регресія)\n\n"
        f"📅 Період аналізу: {days_in_period} днів ({len(all_dates)} точок даних)\n"
        f"💰 Середньомісячний дохід: {avg_month_income:.2f}\n"
        f"💸 Середньомісячні витрати: {avg_month_expense:.2f}\n"
        f"⚖️ Середньомісячний баланс: {avg_month_balance:.2f}\n\n"
        f"🏦 Поточний баланс: {current_balance:.2f}\n"
        f"🔮 Прогноз балансу через {days} днів: {predicted_balance:.2f}\n\n"
        f"📈 ЯКІСТЬ МОДЕЛІ:\n"
        f"R² (витрати) = {r2_expense:.3f}\n"
        f"R² (доходи) = {r2_income:.3f}\n"
        f"Середня похибка витрат: ±{mae_expense:.2f} грн/день\n"
        f"Середня похибка доходів: ±{mae_income:.2f} грн/день\n"
        f"Оцінка: {quality}\n\n"
        f"{status}\n"
        f"💡 {advice}"
    )

    try:
        chart_path = build_forecast_chart(
            expenses_by_day, 
            incomes_by_day, 
            list(expense_pred), 
            list(income_pred),
            expense_upper=list(expense_result['upper_bound'] - expense_pred),
            expense_lower=list(expense_result['lower_bound'] - expense_pred),
            income_upper=list(income_result['upper_bound'] - income_pred),
            income_lower=list(income_result['lower_bound'] - income_pred)
        )
        await message.answer(text)
        await message.answer_photo(FSInputFile(chart_path))
    except Exception as e:
        await message.answer(f"{text}\n\n⚠️ Помилка побудови графіка: {str(e)}")
    
    await state.clear()
