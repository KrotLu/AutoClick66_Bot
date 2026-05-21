"""
Патч для библиотеки maxbot: токен передаётся через заголовок Authorization,
а не через query-параметр access_token (устаревший способ, API возвращает 401).

Запускать один раз после pip install:
    python patch_maxbot.py
"""
import sys
import importlib.util

spec = importlib.util.find_spec("maxbot")
if spec is None:
    print("❌ maxbot не установлен. Сначала выполните: pip install -r requirements.txt")
    sys.exit(1)

import os
bot_path = os.path.join(os.path.dirname(spec.origin), "bot.py")
print(f"Патчим: {bot_path}")

with open(bot_path, "r", encoding="utf-8") as f:
    content = f.read()

patched = False

# ── Патч 1: update_message ──────────────────────────────────────────────────
old1 = (
    '        params = {\n'
    '        "access_token": self.token,\n'
    '        "message_id": message_id,\n'
    '        }'
)
new1 = (
    '        params = {\n'
    '        "message_id": message_id,\n'
    '        }'
)

old1_headers = '        headers={"Content-Type": "application/json"},\n        timeout=httpx.Timeout(30.0)\n        )\n\n\n    async def delete_message'
new1_headers = '        headers={"Content-Type": "application/json", "Authorization": self.token},\n        timeout=httpx.Timeout(30.0)\n        )\n\n\n    async def delete_message'

if old1 in content:
    content = content.replace(old1, new1, 1)
    content = content.replace(old1_headers, new1_headers, 1)
    print("✅ Патч 1 (update_message): применён")
    patched = True
else:
    print("ℹ️  Патч 1 (update_message): уже применён или не нужен")

# ── Патч 2: delete_message ──────────────────────────────────────────────────
old2 = (
    '    async def delete_message(self, message_id: str):\n'
    '        params = {\n'
    '            "access_token": self.token,\n'
    '            "message_id": message_id,\n'
    '        }\n\n'
    '        return await self.client.delete(\n'
    '            f"{self.base_url}/messages",\n'
    '            params=params,\n'
    '            headers={"Content-Type": "application/json"},\n'
    '            timeout=httpx.Timeout(30.0)\n'
    '        )'
)
new2 = (
    '    async def delete_message(self, message_id: str):\n'
    '        params = {\n'
    '            "message_id": message_id,\n'
    '        }\n\n'
    '        return await self.client.delete(\n'
    '            f"{self.base_url}/messages",\n'
    '            params=params,\n'
    '            headers={"Content-Type": "application/json", "Authorization": self.token},\n'
    '            timeout=httpx.Timeout(30.0)\n'
    '        )'
)

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("✅ Патч 2 (delete_message): применён")
    patched = True
else:
    print("ℹ️  Патч 2 (delete_message): уже применён или не нужен")

if patched:
    with open(bot_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("\n✅ Патч успешно применён.")
else:
    print("\nℹ️  Ничего не изменено — патч уже был применён ранее.")
