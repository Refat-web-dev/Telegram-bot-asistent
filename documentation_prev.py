import google.generativeai as genai
import os
import asyncio  # Убедитесь, что asyncio импортирован
from telegram import Update
from telegram.ext import Updater, CallbackContext, ApplicationBuilder, MessageHandler, filters, CommandHandler
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# Настройка Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction="You are a chatbot designed to assist employees with questions about their company. Your name is Astro. Provide clear, concise, and accurate answers based on the company's provided data. If you know the answer to a question without needing the knowledge base, feel free to answer directly. If you encounter a question outside your knowledge base, respond by saying you're unsure about this information and provide company contacts for further assistance. If you receive audio messages, simply repeat the content of the audio word for word. You are speaking with NovaTech employees")

# История чата с информацией о компании
company_info = [
  {"role": "user", "parts": "NovaTech — это инновационная технологическая компания, специализирующаяся на решениях с использованием искусственного интеллекта для бизнеса."},
  {"role": "user", "parts": "Компания NovaTech была основана Refat и Jonibek, двумя опытными программистами и визионерами."},
  {"role": "user", "parts": "NovaTech сотрудничает с партнёрами, такими как School 21, Humans, Uzum и Tenge Bank, чтобы создавать инновационные решения."},
  {"role": "user", "parts": "Вы можете связаться с NovaTech через наш сайт www.refat.ai или по электронной почте contact@jonik.ai."},
  {"role": "user", "parts": "School 21 сотрудничает с NovaTech для разработки образовательных программ и привлечения талантов."},
  {"role": "user", "parts": "Jonibek — талантливый разработчик интерфейсов и соучредитель NovaTech. Он хорошо владеет Python, любит заниматься парсингом создавать Telegram-ботов и пишет интересные книги."},
  {"role": "user", "parts": "Refat — универсальный программист и соучредитель NovaTech. Он специализируется на C/C++, Python, JavaScript, увлекается алгоритмами и ходит в GYM."},
  {"role": "user", "parts": "NovaTech сотрудничает с Tenge Bank для создания безопасных и эффективных финтех-решений."},
  {"role": "user", "parts": "Мы предоставляем комплексные услуги по миграции в облако, чтобы обеспечить плавный переход вашего бизнеса."},
  {"role": "user", "parts": "Флагманским продуктом NovaTech является 'NovaAI' — революционный AI-ассистент для автоматизации бизнес-процессов."},
  {"role": "user", "parts": "Решения NovaTech могут интегрироваться с любыми существующими системами."},
  {"role": "user", "parts": "NovaTech обслуживает такие отрасли, как финансы, здравоохранение, образование, ритейл и другие."},
  {"role": "user", "parts": "NovaTech предлагает решения на основе искусственного интеллекта, услуги по облачной инфраструктуре и разработке программного обеспечения."},
  {"role": "user", "parts": "NovaTech ведет свою деятельность с 2024 года, разрабатывая передовые технологии."},
  {"role": "user", "parts": "Наши решения полностью настраиваемы под нужды клиентов."},
  {"role": "user", "parts": "NovaTech активно поддерживает образовательные инициативы через партнерства, такие как School 21."},
  {"role": "user", "parts": "NovaTech сотрудничала с Uzum в проектах по разработке инструментов на базе AI для анализа клиентов и оптимизации электронной коммерции."},
  {"role": "user", "parts": "Uzum — это проект Refat и Jonibek, созданный как платформа нового поколения для онлайн-шопинга."},
  {"role": "user", "parts": "Штаб-квартира NovaTech находится в Самарканде, а региональные офисы расположены в Европе и Азии."}
]

async def start(update, context):
    await update.message.reply_text("Привет! Я Astro, ваш AI-ассистент. Задайте мне вопрос.")

# Функция для обращения к Gemini API через SDK
async def handle_message(update, context):
    user_question = update.message.text
    
    # Начинаем чат с учетом информации о компании
    chat = model.start_chat(history=company_info)

    # Отправляем вопрос пользователя в чат
    response = chat.send_message(user_question)

    # Ответ модели
    bot_response = response.text
    
    # Отправляем ответ пользователю
    await update.message.reply_text(bot_response)


async def handle_voice(update: Update, context: CallbackContext) -> None:
    voice = update.message.voice

    if voice:
        # Скачиваем файл (асинхронно)
        file_id = voice.file_id
        file = await context.bot.get_file(file_id)  # Добавлено await
        file_path = os.path.join("downloads/", f"tmp_audio.ogg")
        await file.download_to_drive(file_path)  # Используем download_to_drive для сохранения

        myfile = genai.upload_file("downloads/tmp_audio.ogg")

        chat = model.start_chat(history=company_info)
        
        result = model.generate_content(
            [myfile, "\n\n", "repeat the content of the audio word for word"]
        )
        print(f"{result.text=}")

        response = chat.send_message(result.text)
        
        bot_response = response.text

        # Отправляем сообщение пользователю
        await update.message.reply_text(bot_response)

        # Удаляем файл после обработки
        os.remove(file_path)
    

# Главная функция для запуска бота
def main():
    # Создание приложения бота
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Обработчик аудиосообщений
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Запуск бота
    print("Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()