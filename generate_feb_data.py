import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = "finance.db"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Твій Telegram ID
USER_ID = 1011188973

# Отримуємо client_id
cursor.execute("SELECT id FROM clients WHERE telegram_id = ?", (USER_ID,))
result = cursor.fetchone()
if result:
    client_id = result[0]
else:
    print("Користувача не знайдено!")
    exit()

# Отримуємо ID категорій
def get_cat_id(name):
    cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
    result = cursor.fetchone()
    return result[0] if result else None

# Генеруємо дані з 13 січня по 2 лютого 2026
start_date = datetime(2026, 1, 13)
end_date = datetime(2026, 2, 2)

transactions = []
current = start_date

while current <= end_date:
    day = current.day
    month = current.month
    date_str = current.strftime("%Y-%m-%d")
    
    # === ДОХОДИ ===
    
    # Зарплата - 10 числа (вже є за січень, додамо за лютий якщо потрібно)
    # Стипендія - 5 лютого
    if month == 2 and day == 5:
        cat_id = get_cat_id("Стипендія")
        if cat_id:
            transactions.append((client_id, 3500, date_str, cat_id, "income", "Стипендія"))
    
    # Фріланс - випадково
    if random.random() < 0.08:
        cat_id = get_cat_id("Фріланс")
        if cat_id:
            amount = random.choice([2000, 3500, 5000, 8000])
            transactions.append((client_id, amount, date_str, cat_id, "income", "Проект"))
    
    # === ВИТРАТИ ===
    
    # Їжа - кожен день
    cat_id = get_cat_id("Їжа")
    if cat_id:
        food_amount = random.randint(180, 450)
        note = random.choice(["Сільпо", "АТБ", "Обід", "Кава", "Продукти", "Фора"])
        transactions.append((client_id, food_amount, date_str, cat_id, "expense", note))
    
    # Транспорт - будні
    if current.weekday() < 5:
        cat_id = get_cat_id("Транспорт")
        if cat_id:
            transport = random.choice([30, 40, 50, 60, 80])
            note = random.choice(["Метро", "Автобус", "Bolt", "Uklon"])
            transactions.append((client_id, transport, date_str, cat_id, "expense", note))
    
    # Комуналка - 20 січня
    if month == 1 and day == 20:
        cat_id = get_cat_id("Комуналка")
        if cat_id:
            transactions.append((client_id, 2800, date_str, cat_id, "expense", "Комунальні послуги"))
            transactions.append((client_id, 350, date_str, cat_id, "expense", "Інтернет"))
    
    # Розваги - вихідні
    if current.weekday() >= 5:
        if random.random() < 0.5:
            cat_id = get_cat_id("Розваги")
            if cat_id:
                amount = random.randint(200, 600)
                note = random.choice(["Кіно", "Кафе", "Netflix", "Spotify", "Ігри"])
                transactions.append((client_id, amount, date_str, cat_id, "expense", note))
    
    # Здоров'я - рідко
    if random.random() < 0.05:
        cat_id = get_cat_id("Здоров'я")
        if cat_id:
            amount = random.choice([200, 350, 500, 800])
            note = random.choice(["Аптека", "Вітаміни", "Спортзал"])
            transactions.append((client_id, amount, date_str, cat_id, "expense", note))
    
    # Освіта - 1 лютого
    if month == 2 and day == 1:
        cat_id = get_cat_id("Освіта")
        if cat_id:
            transactions.append((client_id, 450, date_str, cat_id, "expense", "Курси Coursera"))
    
    current += timedelta(days=1)

# Додаємо зарплату за лютий (якщо є 2 лютого - рано, але для тесту)
# Краще не додавати, бо 10 лютого ще не настало

# Додаємо всі транзакції
for t in transactions:
    cursor.execute("""
        INSERT INTO transactions (client_id, amount, date, category_id, type, note)
        VALUES (?, ?, ?, ?, ?, ?)
    """, t)

conn.commit()
conn.close()

# Статистика
income_total = sum(t[1] for t in transactions if t[4] == "income")
expense_total = sum(t[1] for t in transactions if t[4] == "expense")

print(f"✅ Додано {len(transactions)} транзакцій")
print(f"📅 Період: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
print(f"💰 Дохід: {income_total:.2f} грн")
print(f"💸 Витрати: {expense_total:.2f} грн")
