import httpx
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# Функция для обращения к Gemini API
def query_gemini(question: str) -> str:
    api_key = "AIzaSyDt-LMAgZxH9a2qq3qWu_I7_aoGbTKQ7m0"  # Замените на ваш API-ключ
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": question}]
        }]
    }
    
    try:
        with httpx.Client(timeout=20.0) as client:  # Увеличили тайм-аут до 20 секунд
            response = client.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Ошибка при обращении к Gemini API."
    except httpx.TimeoutException:
        return "Ошибка: запрос к серверу API не был выполнен вовремя."
    except httpx.ConnectTimeout:
        return "Ошибка: не удалось подключиться к серверу API. Попробуйте снова позже."
    except Exception as e:
        return f"Произошла ошибка: {e}"

async def handle_message(update, context):
    user_question = update.message.text
    bot_response = query_gemini(user_question)
    
    try:
        await update.message.reply_text(bot_response)
    except Exception as e:
        # Дополнительная обработка ошибок при отправке сообщения в Telegram
        print(f"Ошибка при отправке сообщения: {e}")

# Главная функция для запуска бота
def main():
    # Создание приложения бота
    application = ApplicationBuilder().token("8032267077:AAFzehWCIdaNAqPRlAM9L-KsRXBJotJlAxE").build()  # Замените на ваш токен

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    print("Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
