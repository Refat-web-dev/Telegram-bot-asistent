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
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction="Вы чат-бот, помогающий сотрудникам компании с вопросами, общаетесь с сотрудниками UnityELD LogBook. Ваше имя —  Шермат. Если вопрос не касается данных о компании, которыми вы владеете, можете отвечать - свободно. Если вопрос касается данных о компании, но у вас нет нужных данных, сообщите, что не уверены в ответе, и предоставьте контакты компании для дополнительной помощи. При получении аудиосообщений просто повторяйте их содержание дословно. Отвечайте на все вопросы, в контексте — `Дальнобойщиков`.")

# История чата с информацией о компании
company_info = [
  {"role": "user", "parts": "UnityELD LogBook для дальнобойщиков — это электронный журнал или приложение для записи и отслеживания информации, связанной с работой водителей грузовиков."},
  {"role": "user", "parts": "Сервисы для дальнобойщиков включают запись рабочего времени, отслеживание часов вождения, отдыха и времени на загрузку/разгрузку."},
  {"role": "user", "parts": "Предоставляют уведомления о приближении к установленным лимитам, чтобы избежать нарушений."},
  {"role": "user", "parts": "Помогают в соблюдении нормативов, таких как HOS (Hours of Service) в США и других странах, и генерируют отчеты для проверяющих органов."},
  {"role": "user", "parts": "Интеграция с картами и рекомендациями по маршрутам помогает в планировании поездок."},
  {"role": "user", "parts": "Включают учет весовых станций, зон отдыха и мест заправки."},
  {"role": "user", "parts": "Учет расходов на топливо, стоянки, обслуживание и другие статьи затрат с возможностью генерации отчетов по финансам."},
  {"role": "user", "parts": "Дают уведомления о техническом обслуживании, проверке состояния транспортных систем."},
  {"role": "user", "parts": "Хранят электронные копии документов, таких как накладные, счета и страховки, для легкой передачи данных работодателю или инспекторам."},
  {"role": "user", "parts": "Предлагают GPS-трекинг для отслеживания местоположения водителя и транспорта."},
  {"role": "user", "parts": "Включают функции коммуникации с работодателем через чаты и уведомления о сменах, рейсах и других задачах."},
  {"role": "user", "parts": "Интегрируются с ELD (Electronic Logging Device) для автоматического сбора данных о времени в пути и состоянии транспортного средства."},
  {"role": "user", "parts": "Предлагают аналитику и улучшение производительности, включая отчеты по эффективности работы, расходу топлива и другие рекомендации для повышения рентабельности."},
  {"role": "user", "parts": "Вы можете связаться с нами через наш сайт www.refat.ai или по электронной почте contact@jonik.ai."}
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
