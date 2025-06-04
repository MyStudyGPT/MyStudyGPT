import time
import logging
from telebot import TeleBot
from telebot.types import Update
from app import app
from models import db, User, BotMessage, BotStats
from config import TELEGRAM_TOKEN, MAX_FREE_REQUESTS
from openai_helper import get_ai_response

bot = TeleBot(TELEGRAM_TOKEN)

def process_webhook_update(update_dict):
    try:
        update = Update.de_json(update_dict)
        bot.process_new_updates([update])
    except Exception as e:
        logging.error(f"Error processing webhook update: {e}")

def get_or_create_user(message):
    telegram_id = message.from_user.id
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        db.session.add(user)
        db.session.commit()
    return user

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    with app.app_context():
        user = get_or_create_user(message)
        bot.reply_to(message, f"👋 Привет, {user.first_name or 'друг'}! Отправь вопрос, и я помогу.

"
                              f"📊 Использовано: {user.request_count}/{MAX_FREE_REQUESTS}")

@bot.message_handler(commands=['stats'])
def send_stats(message):
    with app.app_context():
        user = get_or_create_user(message)
        bot.reply_to(message, f"📊 Запросов: {user.request_count}/{MAX_FREE_REQUESTS}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    with app.app_context():
        start_time = time.time()
        user = get_or_create_user(message)

        if not user.can_make_request(MAX_FREE_REQUESTS):
            bot.reply_to(message, "⚠️ Лимит запросов исчерпан.")
            return

        try:
            ai_response = get_ai_response(message.text)
            response_time_ms = int((time.time() - start_time) * 1000)
            bot_message = BotMessage(
                user_id=user.id,
                message_text=message.text,
                response_text=ai_response,
                response_time_ms=response_time_ms
            )
            db.session.add(bot_message)
            user.increment_request_count()
            bot.reply_to(message, ai_response)
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка: {str(e)}")

        try:
            stats = BotStats.get_current_stats()
            stats.update_stats()
        except Exception as e:
            logging.error(f"Ошибка статистики: {e}")