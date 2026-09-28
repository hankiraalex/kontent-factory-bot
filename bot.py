import os
import logging
from flask import Flask, request
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена!")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    logger.info("Получен запрос на вебхук")
    try:
        update = telebot.types.Update.de_json(request.get_data(as_text=True))
        bot.process_new_updates([update])
        return '', 200
    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {e}")
        return str(e), 500

@app.route('/')
def index():
    return "Bot is running", 200




