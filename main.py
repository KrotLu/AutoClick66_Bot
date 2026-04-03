import sys
import traceback
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from dotenv import load_dotenv
from handlers import user

# Перехват ошибок импорта для диагностики
try:
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set")
        sys.exit(1)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(user)

except Exception as e:
    print("=" * 50)
    print("ОШИБКА ИНИЦИАЛИЗАЦИИ:")
    traceback.print_exc()
    print("=" * 50)
    sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI started")
    # Устанавливаем вебхук при старте приложения
    # Адрес вебхука — ваш сервер на Render + /webhook
    # Можно задать явно, либо взять из переменной окружения RENDER_EXTERNAL_URL
    webhook_base = os.getenv("RENDER_EXTERNAL_URL", "https://autoclick66-bot.onrender.com")
    webhook_url = f"{webhook_base}/webhook"
    await bot.set_webhook(webhook_url, timeout=30)
    print(f"Webhook set to {webhook_url}")
    yield
    # При остановке удаляем вебхук и закрываем сессию
    await bot.delete_webhook()
    await bot.session.close()
    print("FastAPI stopped")


app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
    
@app.post("/webhook")
async def webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/")
def root():
    return {"status": "ok"}
