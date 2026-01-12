import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = "finance.db"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Telegram ID для демо
DEMO_USER_ID = 1011188973
DEMO_USERNAME = "demo_user"

# Створюємо клієнта
cursor.execute("INSERT OR IGNORE INTO clients (telegram_id, username) VALUES (?, ?)", 
               (DEMO_USER_ID, DEMO_USERNAME))
client_id = cursor.execute("SELECT id FROM clients WHERE telegram_id = ?", (DEMO_USER_ID,)).fetchone()[0]

# Створюємо категорії
categories_expense = [
    ("Їжа", "expense"),
    ("Транспорт", "expense"),
    ("Розваги", "expense"),
    ("Комуналка", "expense"),
    ("Здоров'я", "expense"),
    ("Одяг", "expense"),
    ("Освіта", "expense"),
]

categories_income = [
    ("Зарплата", "income"),
    ("Стипендія", "income"),
    ("Фріланс", "income"),
    ("Інвестиції", "income"),
    ("Подарунки", "income"),
]

for name, cat_type in categories_expense + categories_income:
    cursor.execute("INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)", (name, cat_type))

conn.commit()

# Отримуємо ID категорій
def get_cat_id(name):
    return cursor.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()[0]

# Генеруємо дані за 3 місяці
start_date = datetime(2025, 10, 15)
end_date = datetime(2026, 1, 12)

transactions = []

current = start_date
while current <= end_date:
    day = current.day
    month = current.month
    date_str = current.strftime("%Y-%m-%d")
    
    # === ДОХОДИ ===
    
    # Зарплата - 10 числа кожного місяця
    if day == 10:
        transactions.append((client_id, 45000, date_str, get_cat_id("Зарплата"), "income", "Зарплата за місяць"))
    
    # Стипендія - 5 числа
    if day == 5:
        transactions.append((client_id, 3500, date_str, get_cat_id("Стипендія"), "income", "Стипендія"))
    
    # Фріланс - випадково 2-3 рази на місяць
    if random.random() < 0.1:
        amount = random.choice([2000, 3000, 5000, 7500, 10000])
        transactions.append((client_id, amount, date_str, get_cat_id("Фріланс"), "income", "Проект"))
    
    # === ВИТРАТИ ===
    
    # Їжа - кожен день
    food_amount = random.randint(150, 400)
    transactions.append((client_id, food_amount, date_str, get_cat_id("Їжа"), "expense", random.choice(["Сільпо", "АТБ", "Обід", "Кава", "Продукти"])))
    
    # Транспорт - 5 днів на тиждень
    if current.weekday() < 5:
        transport = random.choice([30, 40, 50, 60, 80])
        transactions.append((client_id, transport, date_str, get_cat_id("Транспорт"), "expense", random.choice(["Метро", "Автобус", "Bolt", "Uklon"])))
    
    # Комуналка - 20 числа
    if day == 20:
        transactions.append((client_id, 2500, date_str, get_cat_id("Комуналка"), "expense", "Комунальні послуги"))
        transactions.append((client_id, 300, date_str, get_cat_id("Комуналка"), "expense", "Інтернет"))
        transactions.append((client_id, 200, date_str, get_cat_id("Комуналка"), "expense", "Мобільний зв'язок"))
    
    # Розваги - вихідні
    if current.weekday() >= 5:
        if random.random() < 0.6:
            amount = random.randint(200, 800)
            transactions.append((client_id, amount, date_str, get_cat_id("Розваги"), "expense", random.choice(["Кіно", "Кафе", "Боулінг", "Концерт", "Netflix"])))
    
    # Здоров'я - раз на 2 тижні
    if random.random() < 0.07:
        amount = random.choice([150, 300, 500, 1000, 2000])
        transactions.append((client_id, amount, date_str, get_cat_id("Здоров'я"), "expense", random.choice(["Аптека", "Лікар", "Спортзал", "Вітаміни"])))
    
    # Одяг - раз на місяць
    if random.random() < 0.03:
        amount = random.choice([500, 1000, 1500, 2000, 3000])
        transactions.append((client_id, amount, date_str, get_cat_id("Одяг"), "expense", random.choice(["Куртка", "Взуття", "Джинси", "Футболка"])))
    
    # Освіта - раз на місяць
    if day == 1:
        transactions.append((client_id, 500, date_str, get_cat_id("Освіта"), "expense", "Курси Udemy"))
    
    current += timedelta(days=1)

# Додаємо всі транзакції
for t in transactions:
    cursor.execute("""
        INSERT INTO transactions (client_id, amount, date, category_id, type, note)
        VALUES (?, ?, ?, ?, ?, ?)
    """, t)

conn.commit()
conn.close()

print(f"✅ Створено {len(transactions)} транзакцій")
print(f"📅 Період: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")

# Статистика
income_total = sum(t[1] for t in transactions if t[4] == "income")
expense_total = sum(t[1] for t in transactions if t[4] == "expense")
print(f"💰 Загальний дохід: {income_total:.2f}")
print(f"💸 Загальні витрати: {expense_total:.2f}")
print(f"⚖️ Баланс: {income_total - expense_total:.2f}")
