import telebot
from config import BOT_TOKEN
from bot_handlers import register_handlers

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
register_handlers(bot)

if __name__ == '__main__':
    print("Бот запущен на Bothost")
    bot.infinity_polling()
