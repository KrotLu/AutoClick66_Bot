import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers import user
from database import init_db   # добавьте импорт

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

async def main():
    # Удаляем старый файл БД, если он существует
    db_path = Path(__file__).parent / "applications.db"
    if db_path.exists():
        os.remove(db_path)
        print("🗑️ Старая база данных удалена")

    # Создаём новую БД и таблицы
    init_db()
    print("✅ Новая база данных создана")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(user)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
