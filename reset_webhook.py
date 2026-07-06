import urllib.request
import json
from config import Config

print("🔄 Очистка вебхука...")

url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/deleteWebhook"

try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        if data.get('ok'):
            print("✅ Вебхук успешно удален!")
            print(f"📡 Ответ: {data}")
        else:
            print(f"❌ Ошибка: {data}")
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")