import os
import threading
import telebot
from flask import Flask

# 1. Получаем токен из переменных окружения (Render)
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("ERROR: BOT_TOKEN is not set in Environment Variables!")
    exit(1)

# 2. Инициализируем бота
bot = telebot.TeleBot(TOKEN)

# 3. КРИТИЧЕСКИ ВАЖНО: Сбрасываем любые старые соединения
# Эта команда обязательна, чтобы избежать ошибки 409
bot.remove_webhook()

# 4. Хендлеры (команды)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот Kontent_Factory. Чем могу помочь?")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Ты написал: {message.text}")

# 5. Flask для Healthcheck (Render требует веб-сервер)
app = Flask(__name__)

@app.route('/')
def health():
    return "OK"

def run_flask():
    port = int(os.getenv('PORT', 5000))
    print(f"Flask running on port {port}")
    app.run(host='0.0.0.0', port=port)

# Запускаем Flask в отдельном потоке
threading.Thread(target=run_flask, daemon=True).start()

# 6. Запуск polling (должен быть строго в самом конце)
print("Starting bot polling...")
try:
    bot.polling(none_stop=True, interval=3)
except Exception as e:
    print(f"Polling error: {e}")
