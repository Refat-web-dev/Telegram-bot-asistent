import os
import time
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events
import google.generativeai as genai
from datetime import datetime, timedelta

# Загрузка переменных окружения
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
gemini_api_key = os.getenv("GEMINI_API_KEY")
target_chat_id = int(os.getenv("TARGET_CHAT_ID"))  # ID группы

# Настройка Gemini
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction=("Ты — чат-бот по имени Astro. Ты вежливый и дружелюбный помощник для людей, которые интересуются IT-школой School 21. Отвечай на основе информации о школе. Если не знаешь ответа — предложи обратиться напрямую в School 21 (предоставь контакты). Если сообщение не выглядит как вопрос или приветствие и никак не относятся к School 21 — возвращай строго фразу: `Вне контекста`. На приветствия отвечай. Целевая аудитория — люди, желающие поступить в School 21.")
)

company_info = [
# ABOUT
  {"role": "user", "parts": "School 21 — это бесплатная IT-школа нового поколения для тех, кто хочет сменить профессию, найти себя в ИТ или получить практические навыки. Обучение построено по принципу «равный обучает равного» — без лекций, менторов и оценок. Вы учитесь через реальные проекты, развиваете софт- и хард-скиллы, сотрудничаете с другими студентами и строите свою образовательную траекторию сами. Школа работает 24/7, можно совмещать с работой или учёбой в вузе. Индивидуальный график, активное профессиональное сообщество, реальные предложения по трудоустройству уже во время обучения — и всё это полностью бесплатно."},
# CONTACTS
  {"role": "user", "parts": "На связи в будни с 10:00 до 19:00."},
  {"role": "user", "parts": "Ташкент, ул. Зиёлилар, 13. (https://yandex.uz/maps/10335/tashkent/house/YkAYdQRlQEUPQFprfX9yeXhnZQ==/?ll=69.334606%2C41.338502&z=17) Ориентир Университет Инха, +998 93 039 4447, tashkent@21-school.uz."},
  {"role": "user", "parts": "Самарканд, ул.Ибн Сино, 17a (https://yandex.ru/maps/org/30165667494), +998930394442,  samarkand@21-school.uz."},
  {"role": "user", "parts": "Зарегистрироваться можно на сайте 21-school.uz (https://21-school.uz/ru/?utm_source=tg&utm_medium=social-organic)."},
]
# Храним чаты и отметки времени
user_chats = {}           # user_id: chat
user_last_active = {}     # user_id: datetime

# Клиент Telethon
client = TelegramClient("session_name", api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    if event.is_private or (event.chat_id == target_chat_id):
        user_input = event.message.message.strip()

        # ⛔ Пропускаем пустые сообщения
        if not user_input:
            return

        user_id = event.sender_id

        if user_id not in user_chats:
            chat = model.start_chat(history=company_info)
            user_chats[user_id] = chat
        else:
            chat = user_chats[user_id]

        user_last_active[user_id] = datetime.now()

        try:
            response = chat.send_message(user_input)
            bot_response = response.text.strip()
        except Exception as e:
            print(f"[Gemini Error]: {e}")
            return

        if bot_response != "Вне контекста":
            await event.reply(bot_response)


# 🕒 Фоновая задача для очистки старых чатов
async def clean_old_chats():
    while True:
        now = datetime.now()
        expired_users = [uid for uid, ts in user_last_active.items() if now - ts > timedelta(hours=1)]

        for uid in expired_users:
            user_chats.pop(uid, None)
            user_last_active.pop(uid, None)
            print(f"❌ Удалена устаревшая сессия пользователя {uid}")

        await asyncio.sleep(3600)  # Проверка каждый час

# 🚀 Запуск
async def main():
    print("Клиент запущен.")
    await client.start()
    asyncio.create_task(clean_old_chats())
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
