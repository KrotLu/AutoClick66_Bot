import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from dotenv import load_dotenv
from handlers import user

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(user)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте (опционально: установка вебхука)
    # Пока закомментируем, чтобы проверить работу сервера
    # webhook_url = "https://autoclick-bot.lubaspv.workers.dev/webhook"
    # await bot.set_webhook(webhook_url)
    print("FastAPI started")
    yield
    # При остановке
    await bot.delete_webhook()
    await bot.session.close()
    print("FastAPI stopped")

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)