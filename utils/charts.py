import matplotlib.pyplot as plt
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

def build_forecast_chart(expense, income, balance):
    plt.figure(figsize=(8, 4))

    plt.plot(expense, label="Витрати")
    plt.plot(income, label="Доходи")
    plt.plot(balance, label="Баланс")

    plt.axhline(0, linestyle="--")
    plt.legend()
    plt.title("Прогноз фінансів")
    plt.tight_layout()

    path = "forecast.png"
    plt.savefig(path)
    plt.close()

    return path
