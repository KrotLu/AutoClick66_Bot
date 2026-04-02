import sqlite3
from datetime import datetime
from pathlib import Path
from filters import state_names

DB_PATH = Path(__file__).parent / "applications.db"


def init_db():
    """Создаёт таблицу для хранения заявок"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Базовые поля
    columns = [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id INTEGER NOT NULL",
        "user_name TEXT NOT NULL",
        "username TEXT",
        "created_at TEXT NOT NULL"
    ]

    # Добавляем поля из state_names (заменяем пробелы на подчёркивания)
    for russian_name in state_names.values():
        safe_name = russian_name.replace(" ", "_")
        columns.append(f"{safe_name} TEXT")

    create_query = f"CREATE TABLE IF NOT EXISTS applications ({', '.join(columns)})"
    cursor.execute(create_query)

    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")


def ensure_table_exists():
    """Проверяет существование таблицы и создаёт её при необходимости"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Проверяем, существует ли таблица
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='applications'")
    if not cursor.fetchone():
        print("⚠️ Таблица не найдена, создаём...")
        conn.close()
        init_db()
    else:
        conn.close()


def save_application(user_data: dict, user) -> int:
    """Сохраняет заявку в базу данных"""
    # Убеждаемся, что таблица существует
    ensure_table_exists()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Формируем данные для вставки
    application_data = {
        "user_id": user.id,
        "user_name": user.full_name,
        "username": user.username,
        "created_at": now
    }

    # Добавляем данные из user_data с заменой пробелов на подчёркивания
    for russian_name in state_names.values():
        safe_name = russian_name.replace(" ", "_")
        application_data[safe_name] = user_data.get(russian_name, "")

    columns = ', '.join(application_data.keys())
    placeholders = ', '.join('?' * len(application_data))

    query = f"INSERT INTO applications ({columns}) VALUES ({placeholders})"
    cursor.execute(query, list(application_data.values()))

    application_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(f"✅ Заявка сохранена с ID: {application_id}")
    return application_id


def get_all_applications(limit: int = 50) -> list:
    """Получает список всех заявок"""
    ensure_table_exists()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applications ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_application_by_id(app_id: int) -> dict:
    """Получает заявку по ID"""
    ensure_table_exists()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def get_applications_count() -> int:
    """Возвращает общее количество заявок"""
    ensure_table_exists()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM applications")
    count = cursor.fetchone()[0]
    conn.close()

    return count