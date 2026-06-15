import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = "finance.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("DELETE FROM transactions")
cursor.execute("DELETE FROM categories")
cursor.execute("DELETE FROM clients")
cursor.execute("DELETE FROM sqlite_sequence")
conn.commit()
print("База очищена")

categories = [
    ("Їжа", "expense"), ("Транспорт", "expense"), ("Розваги", "expense"),
    ("Комуналка", "expense"), ("Здоров'я", "expense"), ("Одяг", "expense"),
    ("Освіта", "expense"), ("Зарплата", "income"), ("Стипендія", "income"),
    ("Фріланс", "income"), ("Інвестиції", "income"), ("Подарунки", "income"),
]

for name, cat_type in categories:
    cursor.execute("INSERT INTO categories (name, type) VALUES (?, ?)", (name, cat_type))
conn.commit()
print(f"Створено {len(categories)} категорій")

USER_ID = 1011188973
cursor.execute("INSERT INTO clients (telegram_id, username) VALUES (?, ?)", (USER_ID, "oleg_minenko"))
client_id = cursor.lastrowid

def get_cat_id(name):
    cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
    return cursor.fetchone()[0]

start_date = datetime(2026, 3, 1)
end_date = datetime(2026, 6, 2)
transactions = []
current = start_date

while current <= end_date:
    day, month, weekday = current.day, current.month, current.weekday()
    date_str = current.strftime("%Y-%m-%d")
    
    if day == 10:
        transactions.append((client_id, 45000, date_str, get_cat_id("Зарплата"), "income", "Зарплата"))
    if day == 5:
        transactions.append((client_id, 3500, date_str, get_cat_id("Стипендія"), "income", "Стипендія"))
    if random.random() < 0.08:
        transactions.append((client_id, random.choice([2000,3000,5000,7000]), date_str, get_cat_id("Фріланс"), "income", "Проект"))
    if random.random() < 0.03:
        transactions.append((client_id, random.choice([500,1000,1500,2000]), date_str, get_cat_id("Інвестиції"), "income", random.choice(["Дивіденди","ETF","Акції"])))
    if random.random() < 0.02:
        transactions.append((client_id, random.choice([500,1000]), date_str, get_cat_id("Подарунки"), "income", "Подарунок"))
    
    transactions.append((client_id, random.randint(180,450), date_str, get_cat_id("Їжа"), "expense", random.choice(["Сільпо","АТБ","Обід","Кава","Продукти"])))
    if random.random() < 0.5:
        transactions.append((client_id, random.randint(80,200), date_str, get_cat_id("Їжа"), "expense", "Кава"))
    
    if weekday < 5:
        transactions.append((client_id, random.choice([30,40,50,60,80]), date_str, get_cat_id("Транспорт"), "expense", random.choice(["Метро","Bolt","Uklon"])))
    
    if day == 20:
        transactions.append((client_id, 2500, date_str, get_cat_id("Комуналка"), "expense", "Комунальні"))
        transactions.append((client_id, 350, date_str, get_cat_id("Комуналка"), "expense", "Інтернет"))
    
    if weekday >= 5 and random.random() < 0.6:
        transactions.append((client_id, random.randint(150,700), date_str, get_cat_id("Розваги"), "expense", random.choice(["Кіно","Кафе","Netflix"])))
    
    if random.random() < 0.05:
        transactions.append((client_id, random.choice([150,300,500]), date_str, get_cat_id("Здоров'я"), "expense", "Аптека"))
    
    if random.random() < 0.025:
        transactions.append((client_id, random.choice([500,1000,1500]), date_str, get_cat_id("Одяг"), "expense", random.choice(["Футболка","Кросівки"])))
    
    if day == 1:
        transactions.append((client_id, random.choice([300,450]), date_str, get_cat_id("Освіта"), "expense", "Курси"))
    
    current += timedelta(days=1)

for t in transactions:
    cursor.execute("INSERT INTO transactions (client_id, amount, date, category_id, type, note) VALUES (?,?,?,?,?,?)", t)

conn.commit()
conn.close()

inc = sum(t[1] for t in transactions if t[4]=="income")
exp = sum(t[1] for t in transactions if t[4]=="expense")
print(f"Період: 01.03.2026 - 02.06.2026")
print(f"Транзакцій: {len(transactions)}")
print(f"Доходи: {inc:,} грн")
print(f"Витрати: {exp:,} грн")
print(f"Баланс: {inc-exp:,} грн")
