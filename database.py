import sqlite3
import os

DB_NAME = "finance.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT CHECK(type IN ('expense', 'income')) NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        date TEXT,
        category_id INTEGER,
        type TEXT CHECK(type IN ('expense', 'income')),
        note TEXT,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    """)
    conn.commit()

def add_category(name, cat_type):
    if not category_exists(name, cat_type):
        cursor.execute(
            "INSERT INTO categories (name, type) VALUES (?, ?)",
            (name, cat_type)
        )
        conn.commit()

def category_exists(name, cat_type):
    return cursor.execute(
        "SELECT 1 FROM categories WHERE name=? AND type=?",
        (name, cat_type)
    ).fetchone() is not None

def get_categories():
    return cursor.execute(
        "SELECT id, name, type FROM categories"
    ).fetchall()

def get_categories_by_type(cat_type):
    return cursor.execute(
        "SELECT id, name FROM categories WHERE type=?",
        (cat_type,)
    ).fetchall()

def add_transaction(user_id, amount, date, category_id, t_type, note):
    cursor.execute("""
        INSERT INTO transactions 
        (user_id, amount, date, category_id, type, note)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, amount, date, category_id, t_type, note))
    conn.commit()

def clear_db():
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM categories")
    conn.commit()

def delete_database():
    global conn, cursor

    conn.close()
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    init_db()

def get_expense_table():
    return cursor.execute("""
        SELECT t.date, c.name, t.amount, t.type, t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.type = 'expense'
        ORDER BY t.date DESC
    """).fetchall()

def get_transactions(user_id, date_from, date_to):
    return cursor.execute("""
        SELECT 
            t.date,
            c.name,
            t.amount,
            t.type,
            t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
          AND t.date BETWEEN ? AND ?
        ORDER BY t.date
    """, (user_id, date_from, date_to)).fetchall()

def get_expenses(user_id):
    """
    Повертає список сум всіх витрат (type='expense') для користувача.
    Використовується для прогнозування.
    """
    return cursor.execute("""
        SELECT amount
        FROM transactions
        WHERE user_id = ? AND type = 'expense'
    """, (user_id,)).fetchall()


def get_expense_by_category(user_id, date_from, date_to):
    return cursor.execute("""
        SELECT c.name, SUM(t.amount)
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
          AND t.type = 'expense'
          AND t.date BETWEEN ? AND ?
        GROUP BY c.name
    """, (user_id, date_from, date_to)).fetchall()

def get_transactions_for_forecast(user_id):
    return cursor.execute("""
        SELECT date, amount, type
        FROM transactions
        WHERE user_id = ?
        ORDER BY date
    """, (user_id,)).fetchall()



def get_all_transactions():
    """Отримати всі транзакції з інформацією про категорії"""
    return cursor.execute("""
        SELECT 
            t.user_id,
            t.date,
            c.name,
            t.amount,
            t.type,
            t.note
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        ORDER BY t.date DESC, t.user_id
    """).fetchall()

def get_user_ids():
    """Отримати список усіх унікальних user_id"""
    return cursor.execute("""
        SELECT DISTINCT user_id 
        FROM transactions 
        ORDER BY user_id
    """).fetchall()

def get_transactions_count():
    """Отримати загальну кількість транзакцій"""
    return cursor.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]

def get_categories_count():
    """Отримати загальну кількість категорій"""
    return cursor.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
