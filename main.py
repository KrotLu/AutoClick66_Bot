import sys
import traceback

try:
    import os
    from contextlib import asynccontextmanager
    from fastapi import FastAPI, Request
    from aiogram import Bot, Dispatcher
    from aiogram.types import Update
    from dotenv import load_dotenv
    from handlers import user  # убедитесь, что это имя правильное
except Exception as e:
    print("=" * 50)
    print("ОШИБКА ИМПОРТА:")
    traceback.print_exc()
    print("=" * 50)
    sys.exit(1)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(user)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI started")
    yield
    await bot.delete_webhook()
    await bot.session.close()
    print("FastAPI stopped")

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}
