import sqlite3
import os
from datetime import datetime

DB_NAME = "finance.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
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
        client_id INTEGER,
        amount REAL,
        date TEXT,
        category_id INTEGER,
        type TEXT CHECK(type IN ('expense', 'income')),
        note TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    """)
    conn.commit()

def get_or_create_client(telegram_id, username=None):
    cursor.execute("SELECT id FROM clients WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    cursor.execute(
        "INSERT INTO clients (telegram_id, username) VALUES (?, ?)",
        (telegram_id, username)
    )
    conn.commit()
    return cursor.lastrowid

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

def add_transaction(user_id, amount, date, category_id, t_type, note, username=None):
    client_id = get_or_create_client(user_id, username)
    cursor.execute("""
        INSERT INTO transactions 
        (client_id, amount, date, category_id, type, note)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (client_id, amount, date, category_id, t_type, note))
    conn.commit()

def clear_db():
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM categories")
    cursor.execute("DELETE FROM clients")
    conn.commit()

def delete_database():
    global conn, cursor

    conn.close()
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    init_db()

def get_transactions(user_id, date_from, date_to):
    client_id = get_or_create_client(user_id)
    return cursor.execute("""
        SELECT 
            t.date,
            c.name,
            t.amount,
            t.type,
            t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        JOIN clients cl ON t.client_id = cl.id
        WHERE cl.telegram_id = ?
          AND t.date BETWEEN ? AND ?
        ORDER BY t.date
    """, (user_id, date_from, date_to)).fetchall()

def get_expense_by_category(user_id, date_from, date_to):
    return cursor.execute("""
        SELECT c.name, SUM(t.amount)
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        JOIN clients cl ON t.client_id = cl.id
        WHERE cl.telegram_id = ?
          AND t.type = 'expense'
          AND t.date BETWEEN ? AND ?
        GROUP BY c.name
    """, (user_id, date_from, date_to)).fetchall()

def get_transactions_for_forecast(user_id):
    return cursor.execute("""
        SELECT t.date, t.amount, t.type
        FROM transactions t
        JOIN clients cl ON t.client_id = cl.id
        WHERE cl.telegram_id = ?
        ORDER BY t.date
    """, (user_id,)).fetchall()

def get_all_transactions():
    return cursor.execute("""
        SELECT 
            cl.telegram_id,
            t.date,
            c.name,
            t.amount,
            t.type,
            t.note
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        LEFT JOIN clients cl ON t.client_id = cl.id
        ORDER BY t.date DESC
    """).fetchall()

def get_user_ids():
    return cursor.execute("""
        SELECT DISTINCT telegram_id 
        FROM clients 
        ORDER BY telegram_id
    """).fetchall()

def get_transactions_count():
    return cursor.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]

def get_categories_count():
    return cursor.execute("SELECT COUNT(*) FROM categories").fetchone()[0]

def get_clients_count():
    return cursor.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
