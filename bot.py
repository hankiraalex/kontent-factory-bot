import os
import logging
import telebot
from telebot import types

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("BOT_TOKEN is not set in Environment Variables!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# --- Фабрика контента (логика) ---
def generate_content(topic, style, format_type):
    """
    Здесь будет логика генерации. Сейчас — шаблоны.
    Позже сюда можно подключить AI, шаблоны из файлов, БД и т.п.
    """
    if format_type == "post":
        return (
            f"📣 Пост по теме: {topic}\n\n"
            f"Стиль: {style}\n\n"
            "🔥 Заголовок: «Как {topic} меняет игру»\n\n"
            "📝 Текст:\n"
            f"Сегодня поговорим про {topic}. Это важно, потому что {style.lower()} подход даёт быстрые результаты.\n\n"
            "💡 Совет: начните с малого и тестируйте каждую гипотезу.\n\n"
            "#{topic.replace(' ', '')} #контент #маркетинг"
        )
    elif format_type == "caption":
        return (
            f"📸 Подпись к фото: {topic}\n"
            f"Тон: {style}\n\n"
            f"{topic} — это про {style.lower()}. Делитесь в комментариях, что вам ближе: быстрый результат или глубина? 👇\n\n"
            "#{topic.replace(' ', '')}"
        )
    elif format_type == "idea":
        return (
            f"💡 Идея контента: {topic}\n"
            f"Подход: {style}\n\n"
            f"Формат: серия из 3 постов.\n"
            f"1. «Что такое {topic} простыми словами»\n"
            f"2. «5 ошибок при работе с {topic}»\n"
            f"3. «Кейс: как мы применили {topic} и что получили»"
        )
    else:
        return f"Контент для {format_type} по теме {topic} в стиле {style} — скоро будет!"

# --- Хендлеры и меню ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_post = types.KeyboardButton("📝 Пост")
    btn_caption = types.KeyboardButton("📸 Подпись")
    btn_idea = types.KeyboardButton("💡 Идея")
    markup.add(btn_post, btn_caption, btn_idea)

    bot.reply_to(
        message,
        "Привет! Я Kontent_Factory — фабрика контента. Выбери тип контента:",
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
    logger.info(f"User requested content type: {content_type}")

    msg = bot.reply_to(
        message,
        f"Отлично! Ты выбрал: {message.text}\nТеперь напиши тему (одним словом или короткой фразой), например: «нейросети», «чай», «велосипед»:\n"
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
        f"Тема: {topic}\nВыбери стиль подачи:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        content_type, topic, style = call.data.split("|")
        logger.info(f"Generating content: type={content_type}, topic={topic}, style={style}")
        result = generate_content(topic, style, content_type)
        bot.edit_message_text(
            text=result,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    except Exception as e:
        logger.exception("Callback error")
        bot.answer_callback_query(call.id, "Произошла ошибка, попробуй ещё раз")

# Запуск polling
if __name__ == '__main__':
    logger.info("Starting bot polling...")
    try:
        bot.polling(none_stop=True, interval=3, skip_pending=True)
    except Exception as e:
        logger.exception(f"Polling error: {e}")
