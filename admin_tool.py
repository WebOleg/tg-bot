import tkinter as tk
from tkinter import messagebox, ttk
import random
from datetime import datetime, timedelta

from database import (
    init_db, clear_db, delete_database,
    add_category, get_categories, get_user_ids,
    add_transaction, get_all_transactions,
    get_transactions_count, get_categories_count
)

# Стилі та кольори
BG_COLOR = "#f0f0f0"
BUTTON_COLOR = "#4a6fa5"
BUTTON_HOVER = "#385d8a"
TEXT_COLOR = "#333333"
HEADER_COLOR = "#2c3e50"
TABLE_HEADER_COLOR = "#34495e"
TABLE_ODD_ROW = "#ffffff"
TABLE_EVEN_ROW = "#f8f9fa"

class HoverButton(tk.Button):
    """Кнопка з ефектом при наведенні"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.default_bg = self['bg']
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        self['bg'] = BUTTON_HOVER
    
    def on_leave(self, e):
        self['bg'] = self.default_bg

# ---------- ЛОГІКА ----------

def init_categories():
    expense = ["Їжа", "Транспорт", "Розваги", "Комуналка", "Здоров'я", "Одяг", "Освіта"]
    income = ["Зарплата", "Стипендія", "Фріланс", "Інвестиції", "Подарунки"]

    for cat in expense:
        add_category(cat, "expense")
    for cat in income:
        add_category(cat, "income")

    refresh_stats()
    messagebox.showinfo("Готово", f"Додано {len(expense) + len(income)} категорій")

def generate_data():
    try:
        user_id = int(user_id_entry.get())
        count = int(transactions_count_entry.get())
    except ValueError:
        messagebox.showerror("Помилка", "Введіть коректні числа для user_id та кількості транзакцій")
        return

    categories = get_categories()
    if not categories:
        messagebox.showerror("Помилка", "Спочатку створіть категорії")
        return

    start_date = datetime.now() - timedelta(days=90)
    
    for _ in range(count):
        amount = random.randint(50, 10000)
        # Теперь ВСЕГДА в формате YYYY-MM-DD
        date = (start_date + timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d")
        category_id, _, cat_type = random.choice(categories)
        notes = ["Покупка", "Оплата", "Переказ", "Зняття", "Поповнення", "", "Регулярний платіж"]
        note = random.choice(notes)

        add_transaction(user_id, amount, date, category_id, cat_type, note)

    refresh_table()
    refresh_stats()
    messagebox.showinfo("Готово", f"Згенеровано {count} транзакцій для user_id {user_id}")

def clear_database():
    if messagebox.askyesno("Підтвердження", "Ви впевнені, що хочете видалити всі дані?\nЦя операція незворотна."):
        clear_db()
        refresh_table()
        refresh_stats()
        messagebox.showinfo("Готово", "Всі дані видалено")

def delete_db():
    if messagebox.askyesno("Підтвердження", "Ви впевнені, що хочете видалити всю базу даних?\nБуде створена нова порожня база."):
        delete_database()
        refresh_table()
        refresh_stats()
        messagebox.showinfo("Готово", "Базу даних перестворено")

def refresh_table():
    try:
        # Очищення таблиці
        for row in table.get_children():
            table.delete(row)

        # Отримання даних
        rows = get_all_transactions()
        
        # Заповнення таблиці
        for i, r in enumerate(rows):
            tag = 'even' if i % 2 == 0 else 'odd'
            table.insert("", tk.END, values=r, tags=(tag,))

    except Exception as e:
        messagebox.showerror(
            "Помилка завантаження даних",
            f"Не вдалося завантажити дані:\n{str(e)}"
        )

def refresh_stats():
    """Оновлення статистики"""
    try:
        total_transactions = get_transactions_count()
        total_categories = get_categories_count()
        users = get_user_ids()
        
        stats_label.config(
            text=f"📊 Статистика: {total_transactions} транзакцій | "
                 f"{total_categories} категорій | "
                 f"{len(users)} користувачів"
        )
    except Exception as e:
        stats_label.config(text=f"📊 Статистика: помилка - {str(e)}")

def filter_by_user():
    """Фільтрація за user_id"""
    try:
        filter_id = user_filter_entry.get()
        if not filter_id:
            refresh_table()
            return
            
        user_id = int(filter_id)
        
        # Отримання всіх даних та фільтрація
        rows = get_all_transactions()
        
        # Очищення таблиці
        for row in table.get_children():
            table.delete(row)
        
        # Заповнення відфільтрованими даними
        for i, r in enumerate(rows):
            if r[0] == user_id:  # r[0] - це user_id
                tag = 'even' if i % 2 == 0 else 'odd'
                table.insert("", tk.END, values=r, tags=(tag,))
                
    except ValueError:
        messagebox.showerror("Помилка", "Введіть коректний user_id")
    except Exception as e:
        messagebox.showerror("Помилка", f"Помилка фільтрації: {str(e)}")

# ---------- ІНТЕРФЕЙС ----------

init_db()

root = tk.Tk()
root.title("💰 Адмін-панель Finance Bot")
root.geometry("1200x700")
root.configure(bg=BG_COLOR)

# Встановлюємо стиль для ttk
style = ttk.Style()
style.theme_use('clam')

# Налаштовуємо кольори для Treeview
style.configure("Treeview",
                background=TABLE_ODD_ROW,
                foreground=TEXT_COLOR,
                rowheight=25,
                fieldbackground=TABLE_ODD_ROW)
style.map('Treeview', background=[('selected', '#347083')])

style.configure("Treeview.Heading",
                background=TABLE_HEADER_COLOR,
                foreground="white",
                relief="flat",
                font=('Arial', 10, 'bold'))
style.map("Treeview.Heading",
          background=[('active', '#1abc9c')])

# --- Заголовок ---
header_frame = tk.Frame(root, bg=HEADER_COLOR, height=80)
header_frame.pack(fill=tk.X)
header_frame.pack_propagate(False)

tk.Label(header_frame,
         text="💰 Адміністративна панель Finance Bot",
         font=('Arial', 20, 'bold'),
         fg='white',
         bg=HEADER_COLOR).pack(pady=20)

# --- Панель статистики ---
stats_frame = tk.Frame(root, bg=BG_COLOR)
stats_frame.pack(fill=tk.X, pady=(10, 5), padx=20)

stats_label = tk.Label(stats_frame,
                      text="📊 Статистика: завантаження...",
                      font=('Arial', 10),
                      fg=TEXT_COLOR,
                      bg=BG_COLOR)
stats_label.pack()

refresh_stats()

# --- Панель керування ---
control_frame = tk.Frame(root, bg=BG_COLOR, relief=tk.RAISED, borderwidth=1)
control_frame.pack(fill=tk.X, padx=20, pady=10)

# Ліва частина - ввід даних
left_control = tk.Frame(control_frame, bg=BG_COLOR)
left_control.grid(row=0, column=0, padx=10, pady=10, sticky='w')

tk.Label(left_control, text="User ID:", bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, padx=5)
user_id_entry = tk.Entry(left_control, width=15)
user_id_entry.grid(row=0, column=1, padx=5)
user_id_entry.insert(0, "1")

tk.Label(left_control, text="Кількість транзакцій:", bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=2, padx=5)
transactions_count_entry = tk.Entry(left_control, width=15)
transactions_count_entry.grid(row=0, column=3, padx=5)
transactions_count_entry.insert(0, "50")

# Права частина - кнопки дій
right_control = tk.Frame(control_frame, bg=BG_COLOR)
right_control.grid(row=0, column=1, padx=10, pady=10, sticky='e')

buttons = [
    ("🔄 Оновити таблицю", refresh_table),
    ("📁 Створити категорії", init_categories),
    ("🎲 Згенерувати дані", generate_data),
    ("🧹 Очистити дані", clear_database),
    ("🗑️ Видалити БД", delete_db)
]

for i, (text, command) in enumerate(buttons):
    btn = HoverButton(right_control,
                      text=text,
                      command=command,
                      bg=BUTTON_COLOR,
                      fg='white',
                      font=('Arial', 9),
                      padx=15,
                      pady=5,
                      cursor='hand2',
                      relief=tk.FLAT)
    btn.grid(row=0, column=i, padx=3)

# --- Панель фільтрації ---
filter_frame = tk.Frame(root, bg=BG_COLOR)
filter_frame.pack(fill=tk.X, padx=20, pady=5)

tk.Label(filter_frame,
         text="Фільтр за User ID:",
         bg=BG_COLOR,
         fg=TEXT_COLOR,
         font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

user_filter_entry = tk.Entry(filter_frame, width=15)
user_filter_entry.pack(side=tk.LEFT, padx=5)

filter_btn = HoverButton(filter_frame,
                         text="Застосувати фільтр",
                         command=filter_by_user,
                         bg=BUTTON_COLOR,
                         fg='white',
                         font=('Arial', 9),
                         padx=10,
                         pady=2,
                         cursor='hand2')
filter_btn.pack(side=tk.LEFT, padx=5)

clear_filter_btn = HoverButton(filter_frame,
                               text="Скинути фільтр",
                               command=refresh_table,
                               bg="#95a5a6",
                               fg='white',
                               font=('Arial', 9),
                               padx=10,
                               pady=2,
                               cursor='hand2')
clear_filter_btn.pack(side=tk.LEFT, padx=5)

# --- Таблиця ---
table_frame = tk.Frame(root, bg=BG_COLOR)
table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))

# Створюємо скролбари
scroll_y = ttk.Scrollbar(table_frame)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

# Створюємо таблицю
columns = ("User ID", "Дата", "Категорія", "Сума", "Тип", "Примітка")
table = ttk.Treeview(table_frame,
                     columns=columns,
                     show="headings",
                     yscrollcommand=scroll_y.set,
                     xscrollcommand=scroll_x.set)

# Налаштовуємо заголовки
column_widths = [80, 100, 150, 100, 100, 200]
for col, width in zip(columns, column_widths):
    table.heading(col, text=col)
    table.column(col, width=width, anchor=tk.CENTER)

# Конфігуруємо скролбари
scroll_y.config(command=table.yview)
scroll_x.config(command=table.xview)

# Упаковуємо таблицю
table.pack(fill=tk.BOTH, expand=True)

# Налаштовуємо теги для парних/непарних рядків
table.tag_configure('odd', background=TABLE_ODD_ROW)
table.tag_configure('even', background=TABLE_EVEN_ROW)

# --- Нижній колонтитул ---
footer_frame = tk.Frame(root, bg=HEADER_COLOR, height=40)
footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
footer_frame.pack_propagate(False)

tk.Label(footer_frame,
         text="© Finance Bot Admin Tool",
         font=('Arial', 8),
         fg='white',
         bg=HEADER_COLOR).pack(pady=10)

# --- Ініціалізація ---
refresh_table()

# Запуск головного циклу
root.mainloop()
