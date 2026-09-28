import os
import logging
import telebot
from flask import Flask, request
from telebot import types

# 1. Настройка логирования (Render читает именно логи, а не print)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# 2. Получение токена
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("BOT_TOKEN is not set in Environment Variables!")
    exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


# --- Логика Контент-завода ---
def generate_content(topic, style, format_type):
    if format_type == "post":
        return (
            f"📣 Пост по теме: {topic}\n\n"
            f"Стиль: {style}\n\n"
            "🔥 Заголовок: «Как {topic} меняет игру»\n\n"
            "📝 Текст:\n"
            f"Сегодня поговорим про {topic}. Это важно, потому что {style.lower()} подход даёт быстрые результаты.\n\n"
            "💡 Совет: начните с малого и тестируйте каждую гипотезу.\n\n"
            "#{topic.replace(' ', '')} #контент #маркетинг"
        ).format(topic=topic, style=style)
    elif format_type == "caption":
        return (
            f"📸 Подпись к фото: {topic}\n"
            f"Тон: {style}\n\n"
            f"{topic} — это про {style.lower()}. Делитесь в комментариях, что вам ближе? 👇\n\n"
            "#{topic.replace(' ', '')}"
        ).format(topic=topic, style=style)
    elif format_type == "idea":
        return (
            f"💡 Идея контента: {topic}\n"
            f"Подход: {style}\n\n"
            f"Формат: серия из 3 постов.\n"
            f"1. «Что такое {topic} простыми словами»\n"
            f"2. «5 ошибок при работе с {topic}»\n"
            f"3. «Кейс: как мы применили {topic} и что получили»"
        ).format(topic=topic, style=style)
    return "Контент скоро будет!"


# --- Хендлеры ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_post = types.KeyboardButton("📝 Пост")
    btn_caption = types.KeyboardButton("📸 Подпись")
    btn_idea = types.KeyboardButton("💡 Идея")
    markup.add(btn_post, btn_caption, btn_idea)

    bot.reply_to(
        message,
        "Привет! Я Kontent_Factory. Выбери тип контента:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text in ["📝 Пост", "📸 Подпись", "💡 Идея"])
def handle_content_type(message):
    content_map = {
        "📝 Пост": "post",
        "📸 Подпись": "caption",
        "💡 Идея": "idea"
    }
    content_type = content_map[message.text]
    logger.info(f"User requested: {content_type}")

    msg = bot.reply_to(
        message,
        f"Отлично! Ты выбрал: {message.text}\nНапиши тему (одним словом):"
    )
    bot.register_next_step_handler(msg, lambda m: ask_style(m, content_type))


def ask_style(message, content_type):
    topic = message.text
    markup = types.InlineKeyboardMarkup()
    styles = [
        ("Официально", "official"),
        ("Дружелюбно", "friendly"),
        ("Экспертно", "expert"),
        ("С юмором", "funny")
    ]
    for text, callback in styles:
        markup.add(types.InlineKeyboardButton(text, callback_data=f"{content_type}|{topic}|{callback}"))

    bot.reply_to(
        message,
        f"Тема: {topic}\nВыбери стиль:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        content_type, topic, style = call.data.split("|")
        result = generate_content(topic, style, content_type)
        bot.edit_message_text(
            text=result,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    except Exception as e:
        logger.exception("Callback error")
        bot.answer_callback_query(call.id, "Ошибка, попробуй ещё раз")


# --- Flask и Webhook (Критично для Render) ---
@app.route('/')
def health():
    return "OK"


@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return '', 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting Flask on port {port}")
    app.run(host='0.0.0.0', port=port)

