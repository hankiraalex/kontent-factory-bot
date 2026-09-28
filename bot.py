import os
import logging
from flask import Flask, request
import telebot
from telebot import types

# 1. Получаем токен ДО определения маршрутов
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена!")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# 2. Маршрут для вебхука
# Используем статическую строку или переменную, которая уже точно определена
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    logger.info("Получен запрос на вебхук")
    try:
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return '', 200
    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {e}")
        return str(e), 500

# 3. Главная страница (нужна, чтобы Render видел, что сервис жив)
@app.route('/')
def index():
    return "Bot is running", 200



