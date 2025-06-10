import os
import time

from dotenv import load_dotenv
from telethon import TelegramClient, events
import google.generativeai as genai

# Загрузка переменных
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
gemini_api_key = os.getenv("GEMINI_API_KEY")
target_chat_id = int(os.getenv("TARGET_CHAT_ID"))  # ID чата (группы)

# Настройка Gemini
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction="Ты — чат-бот по имени Astro. Помогаешь людям, которые интересуются поступлением в IT-школу School 21. Отвечай чётко, кратко и по делу, только на основе информации о школе. Если знаешь ответ — отвечай напрямую. Если не знаешь — скажи, что не уверен, и предложи обратиться в School 21 напрямую. Если получаешь аудио — просто повтори его дословно. Если получаешь сообщение, не являющееся вопросом, не относящееся к поступлению в School 21 или вне контекста — возвращай строго фразу: 'Вне контекста'. Целевая аудитория — люди, желающие поступить в School 21."
)

company_info = [
# ABOUT
  {"role": "user", "parts": "Ссылки: Telegram - https://t.me/skd21school?roistat_visit=2580615, Instagram - https://www.instagram.com/school.21_uz?roistat_visit=2580615, Youtube - https://www.youtube.com/@School21.Uzbekistan?roistat_visit=2580615, LinkedIn - https://www.linkedin.com/company/digital-engineering-school-21?roistat_visit=2580615, Facebook - https://www.facebook.com/share/AvKQEzG9asoC3Epd/?mibextid=JRoKGi&roistat_visit=2580615 ."},
]

# Создаем клиент
client = TelegramClient("session_name", api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    if event.is_private or (event.chat_id == target_chat_id):
        user_input = event.message.message

        # Создаём чат с историей
        chat = model.start_chat(history=company_info)
        response = chat.send_message(user_input)

        bot_response = response.text.strip()
        if "Вне контекста" not in bot_response:
            await event.reply(bot_response)
# # Ответ модели
#     bot_response = response.text

# # Отправляем ответ пользователю
#     await event.reply(response.text)
# Запуск клиента
print("Клиент запущен")
client.start()
while True:
    try:
        client.run_until_disconnected()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        time.sleep(5)

