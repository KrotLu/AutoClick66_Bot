import sys
import os
import re
import importlib.util

def patch_file(bot_path):
    print(f"Найден: {bot_path}")
    with open(bot_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    changes = []
    # Патч 1: update_message (ищем блок с access_token)
    pattern1 = r'(params\s*=\s*\{\s*"access_token":\s*self\.token,\s*"message_id":\s*message_id,\s*\})'
    if re.search(pattern1, content):
        content = re.sub(pattern1, 'params = {"message_id": message_id}', content)
        changes.append("Убран access_token из params (update_message)")
    # Патч 2: delete_message
    pattern2 = r'(params\s*=\s*\{\s*"access_token":\s*self\.token,\s*"message_id":\s*message_id,\s*\})'
    if re.search(pattern2, content):
        content = re.sub(pattern2, 'params = {"message_id": message_id}', content)
        changes.append("Убран access_token из params (delete_message)")
    # Добавляем Authorization в headers, если отсутствует
    header_pattern = r'headers=\{"Content-Type":\s*"application/json"\}'
    if re.search(header_pattern, content) and 'Authorization' not in re.search(header_pattern, content).group():
        content = re.sub(header_pattern, 'headers={"Content-Type": "application/json", "Authorization": self.token}', content)
        changes.append("Добавлен Authorization в headers")
    
    if changes:
        with open(bot_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("\n".join(changes))
        # Очищаем __pycache__
        pycache = os.path.join(os.path.dirname(bot_path), "__pycache__")
        if os.path.exists(pycache):
            for f in os.listdir(pycache):
                if f.endswith(".pyc"):
                    os.remove(os.path.join(pycache, f))
            print("Очищен __pycache__")
        return True
    else:
        print("ℹ️  access_token не найден — патч уже был применён ранее.")
        return False

# Ищем maxbot или umaxbot
def find_and_patch():
    for lib_name in ["maxbot", "umaxbot"]:
        spec = importlib.util.find_spec(lib_name)
        if spec is None:
            continue
        bot_path = os.path.join(os.path.dirname(spec.origin), "bot.py")
        if os.path.exists(bot_path):
            return patch_file(bot_path)
    print("❌ Не найден ни maxbot, ни umaxbot")
    return False

if __name__ == "__main__":
    if find_and_patch():
        print("✅ Патч успешно применён. Перезапустите бота.")
    else:
        print("❌ Патч не применён.")
