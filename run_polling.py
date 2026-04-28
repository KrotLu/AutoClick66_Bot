import asyncio
import os
from pathlib import Path
from obabot import create_bot
from handlers import user
from database import init_db
from keep_alive import keep_alive

db_path = Path(__file__).parent / "applications.db"
if db_path.exists():
    os.remove(db_path)
    print("🗑️ Старая база данных удалена")

init_db()

BOT_TOKEN = os.environ["BOT_TOKEN"]
MAX_TOKEN = os.environ.get("MAX_BOT_TOKEN")


def _populate_pending_handlers(proxy_router, aiogram_router):
    """Переносит обработчики из aiogram Router в ProxyRouter._pending_handlers для MAX."""
    for h in aiogram_router.message.handlers:
        filters = tuple(fo.callback for fo in h.filters)
        proxy_router._pending_handlers.append(("message", filters, {}, h.callback))
    for h in aiogram_router.callback_query.handlers:
        filters = tuple(fo.callback for fo in h.filters)
        proxy_router._pending_handlers.append(
            ("callback_query", filters, {}, h.callback)
        )


async def main():
    if MAX_TOKEN:
        bot, dp, proxy_router = create_bot(tg_token=BOT_TOKEN, max_token=MAX_TOKEN)
        print("✅ Бот запущен в режиме Telegram + MAX")
    else:
        bot, dp, proxy_router = create_bot(tg_token=BOT_TOKEN)
        print("✅ Бот запущен только в Telegram (MAX не настроен)")

    for platform in dp._platforms:
        ensure_inited = getattr(platform, "_ensure_inited", None)
        if ensure_inited is None:
            continue

        platform_type = getattr(platform, "_platform_type", None)

        if platform_type == "telegram":
            real = ensure_inited()
            inner_router = getattr(real, "_router", None)
            if inner_router is not None and hasattr(inner_router, "include_router"):
                inner_router.include_router(user)

        elif platform_type == "max":
            _populate_pending_handlers(proxy_router, user)
            ensure_inited()

    await dp.start_polling(bot)


if __name__ == "__main__":
    keep_alive()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
