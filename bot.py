import os
import threading
import telebot
from flask import Flask

# 1. Сначала читаем переменные и проверяем их
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("ERROR: BOT_TOKEN is not set!")
    exit(1)  # Принудительно завершаем работу, если токена нет

# 2. Инициализируем бота только после проверки токена
bot = telebot.TeleBot(TOKEN)

# 3. Регистрируем хендлеры (команды)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот Kontent_Factory. Чем могу помочь?")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Ты написал: {message.text}")

# 4. Настраиваем Flask (только для проверки здоровья Render)
app = Flask(__name__)

@app.route('/')
def health():
    return "OK"

def run_flask():
    # ВАЖНО: Render сам назначает порт. Мы обязаны его прочитать.
    port = int(os.getenv('PORT', 5000))
    print(f"Flask running on port {port}")
    app.run(host='0.0.0.0', port=port)

# Запускаем Flask в отдельном потоке (daemon=True обязателен)
threading.Thread(target=run_flask, daemon=True).start()

# 5. Запускаем polling только в самом конце
print("Bot is polling...")
bot.polling(none_stop=True, interval=3)

