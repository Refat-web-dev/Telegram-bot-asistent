import os
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
target_chat_id = int(os.getenv("TARGET_CHAT_ID"))

# Настройка Gemini
genai.configure(api_key=gemini_api_key)

# Массив моделей
MODEL_NAMES = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.0-flash",
    "gemma-3",
    "gemma-3n"
]

# Инициализация моделей
MODELS = []
for name in MODEL_NAMES:
    try:
        model = genai.GenerativeModel(name, 
                                      system_instruction=("Ты — чат-бот по имени Astro. "
                    "Ты разговариваешь на всех языках мира."
                    "Отвечай только на сообщения, относящиеся к School 21. "
                    "Если не уверен — направляй в School 21 (контакты у тебя есть) и к саппорту @Zoidov_Zafarjon. "
                    "Если сообщение не связано с School 21 и не является приветствием — ответь строго: `__IGNORE__`."))
        MODELS.append((name, model))
    except Exception as e:
        print(f"[Ошибка при инициализации модели {name}]: {e}")

# Текущая активная модель
current_model_index = 0

# Контекст компании
company_info = [{
    "role": "user",
    "parts": (
        "School 21 — это бесплатная IT-школа нового поколения..."
    )
}]

user_chats = {}
user_last_active = {}
client = TelegramClient("session_name", api_id, api_hash)

async def switch_model():
    global current_model_index
    current_model_index = (current_model_index + 1) % len(MODELS)
    print(f"🔁 Переключение на модель: {MODELS[current_model_index][0]}")

@client.on(events.NewMessage)
async def handler(event):
    global current_model_index

    if event.is_private or (event.chat_id == target_chat_id):
        user_input = event.message.message.strip()
        if not user_input:
            return

        user_id = event.sender_id
        model_name, model = MODELS[current_model_index]

        try:
            if user_id not in user_chats:
                chat = model.start_chat(history=company_info)
                user_chats[user_id] = chat
            else:
                chat = user_chats[user_id]

            user_last_active[user_id] = datetime.now()

            chat.history.append({
                "role": "user",
                "parts": (
                    "Ты — чат-бот по имени Astro. "
                    "Ты разговариваешь на всех языках мира."
                    "Отвечай только на сообщения, относящиеся к School 21. "
                    "Если не уверен — направляй в School 21 (контакты у тебя есть). "
                    "Если сообщение не связано с School 21 и не является приветствием — ответь строго: `__IGNORE__`."
                )
            })

            response = chat.send_message(user_input)
            bot_response = response.text.strip()

            if "__IGNORE__" in bot_response:
                return

            await event.reply(bot_response)

        except Exception as e:
            print(f"[Gemini Error with {model_name}]: {e}")
            if "429" in str(e):
                await switch_model()

async def clean_old_chats():
    while True:
        now = datetime.now()
        expired_users = [uid for uid, ts in user_last_active.items() if now - ts > timedelta(hours=1)]
        for uid in expired_users:
            user_chats.pop(uid, None)
            user_last_active.pop(uid, None)
            print(f"❌ Удалена устаревшая сессия пользователя {uid}")
        await asyncio.sleep(3600)

async def main():
    print("Клиент запущен.")
    await client.start()
    asyncio.create_task(clean_old_chats())
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
