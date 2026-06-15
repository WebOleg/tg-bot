import matplotlib.pyplot as plt
import numpy as np
import uuid


def expense_pie_chart(data):
    labels = [row[0] for row in data]
    sizes = [row[1] for row in data]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title("Структура витрат")
    filename = f"chart_{uuid.uuid4().hex}.png"
    plt.savefig(filename)
    plt.close()
    return filename


def build_forecast_chart(historical_expenses, historical_incomes, 
                        forecast_expenses, forecast_incomes,
                        expense_upper=None, expense_lower=None,
                        income_upper=None, income_lower=None):
    plt.figure(figsize=(12, 6))
    
    hist_len = len(historical_expenses)
    fore_len = len(forecast_expenses)
    
    hist_x = list(range(hist_len))
    fore_x = list(range(hist_len, hist_len + fore_len))
    
    # Накопичені фактичні значення
    hist_cum_exp = np.cumsum(historical_expenses)
    hist_cum_inc = np.cumsum(historical_incomes)
    hist_cum_bal = hist_cum_inc - hist_cum_exp
    
    last_exp = hist_cum_exp[-1] if len(hist_cum_exp) > 0 else 0
    last_inc = hist_cum_inc[-1] if len(hist_cum_inc) > 0 else 0
    
    # Накопичені прогнозні значення
    fore_cum_exp = last_exp + np.cumsum(forecast_expenses)
    fore_cum_inc = last_inc + np.cumsum(forecast_incomes)
    fore_cum_bal = fore_cum_inc - fore_cum_exp
    
    # ФАКТИЧНІ ДАНІ (суцільні лінії)
    plt.plot(hist_x, hist_cum_exp, color="red", linewidth=2, label="Витрати (факт)")
    plt.plot(hist_x, hist_cum_inc, color="green", linewidth=2, label="Доходи (факт)")
    plt.plot(hist_x, hist_cum_bal, color="blue", linewidth=2, label="Баланс (факт)")
    
    # ПРОГНОЗ (пунктирні лінії)
    plt.plot(fore_x, fore_cum_exp, color="red", linewidth=2, linestyle="--", label="Витрати (прогноз)")
    plt.plot(fore_x, fore_cum_inc, color="green", linewidth=2, linestyle="--", label="Доходи (прогноз)")
    plt.plot(fore_x, fore_cum_bal, color="blue", linewidth=2, linestyle="--", label="Баланс (прогноз)")
    
    # ДОВІРЧИЙ ІНТЕРВАЛ (похибка прогнозу)
    if expense_upper is not None and expense_lower is not None:
        upper_cum = last_exp + np.cumsum(expense_upper)
        lower_cum = last_exp + np.cumsum(expense_lower)
        plt.fill_between(fore_x, lower_cum, upper_cum, color="red", alpha=0.15, 
                        label="Похибка витрат (95% CI)")
    
    if income_upper is not None and income_lower is not None:
        upper_cum = last_inc + np.cumsum(income_upper)
        lower_cum = last_inc + np.cumsum(income_lower)
        plt.fill_between(fore_x, lower_cum, upper_cum, color="green", alpha=0.15,
                        label="Похибка доходів (95% CI)")
    
    # Вертикальна лінія "Сьогодні"
    plt.axvline(x=hist_len-1, color="gray", linestyle=":", alpha=0.7, label="Сьогодні")
    plt.axhline(0, linestyle="--", color="gray", alpha=0.3)
    
    # Заливка балансу
    plt.fill_between(hist_x, hist_cum_bal, 0, alpha=0.2, color="blue")
    plt.fill_between(fore_x, fore_cum_bal, 0, alpha=0.1, color="blue")
    
    plt.legend(loc="upper left", fontsize=8)
    plt.title("Фінансовий прогноз з довірчим інтервалом (95% CI)")
    plt.xlabel("Дні")
    plt.ylabel("Сума (грн)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    path = "forecast.png"
    plt.savefig(path)
    plt.close()
    return path
