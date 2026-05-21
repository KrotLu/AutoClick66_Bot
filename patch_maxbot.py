import site
import os
import re

def patch_bot(lib_name):
    for path in site.getsitepackages():
        bot_file = os.path.join(path, lib_name, 'bot.py')
        if not os.path.exists(bot_file):
            continue
        print(f"Патчим {bot_file}")
        with open(bot_file, 'r') as f:
            content = f.read()
        # Проверяем, нужен ли патч (есть access_token в params)
        if 'access_token' in content and 'Authorization' not in content:
            # Убираем access_token из params
            content = re.sub(r',?\s*"access_token": self\.token,?\s*', '', content)
            # Добавляем Authorization в headers там, где его нет
            content = re.sub(
                r'headers={"Content-Type": "application/json"}',
                'headers={"Content-Type": "application/json", "Authorization": self.token}',
                content
            )
            content = re.sub(
                r'headers=\{"Content-Type": "application/json"\}',
                'headers={"Content-Type": "application/json", "Authorization": self.token}',
                content
            )
            with open(bot_file, 'w') as f:
                f.write(content)
            print(f"✅ Патч применён к {lib_name}")
            return True
        else:
            print(f"ℹ️ {lib_name} уже использует Authorization или не требует патча")
            return False
    return False

if __name__ == "__main__":
    patched = patch_bot('umaxbot') or patch_bot('maxbot')
    if not patched:
        print("❌ Не удалось найти ни umaxbot, ни maxbot. Установите зависимости сначала.")
    else:
        print("✅ Патч успешно применён.")
