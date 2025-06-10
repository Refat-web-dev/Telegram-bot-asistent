import google.generativeai as genai
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, CallbackContext
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Настройка Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction="Вы чат-бот, помогающий сотрудникам компании NovaTech с вопросами.Все, кто вам пишет сотрудники NowaTech. Ваше имя — Astro. Если вопрос не касается данных о компании, которыми вы владеете, можете отвечать - свободно. Если вопрос касается данных о компании, но у вас нет нужных данных, сообщите, что не уверены в ответе, и предоставьте контакты компании для дополнительной помощи. При получении аудиосообщений просто повторяйте их содержание дословно. Вы знаете все языки мира.")

# Хранилище истории чатов пользователей
chat_histories = {}

# Базовая информация о компании
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
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Я Astro, ваш AI-ассистент. Задайте мне вопрос.")

async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_text = update.message.text

    # Если у пользователя нет истории, создаем её
    if user_id not in chat_histories:
        chat_histories[user_id] = company_info.copy()
    
    # Добавляем вопрос пользователя в историю
    chat_histories[user_id].append({"role": "user", "parts": user_text})
    
    try:
        # Создаем чат с историей
        chat = model.start_chat(history=chat_histories[user_id])
        response = chat.send_message(user_text)
        bot_response = response.text
    except Exception as e:
        bot_response = "Извините, возникла ошибка при обработке запроса. Попробуйте позже."
        print(f"Ошибка: {e}")
    
    # Добавляем ответ бота в историю
    chat_histories[user_id].append({"role": "model", "parts": bot_response})
    
    await update.message.reply_text(bot_response)

async def handle_voice(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    voice = update.message.voice

    if voice:
        file_id = voice.file_id
        file = await context.bot.get_file(file_id)
        file_path = f"downloads/{user_id}_audio.ogg"
        await file.download_to_drive(file_path)
        
        try:
            # Загружаем аудиофайл в Gemini
            myfile = genai.upload_file(file_path)
            chat = model.start_chat(history=chat_histories.get(user_id, company_info))
            result = model.generate_content([myfile, "\n\n", "repeat the content of the audio word for word"])
            transcript = result.text.strip()
        
            # Добавляем расшифровку в историю
            chat_histories.setdefault(user_id, company_info.copy()).append({"role": "user", "parts": transcript})
            response = chat.send_message(transcript)
            bot_response = response.text
            chat_histories[user_id].append({"role": "model", "parts": bot_response})
        except Exception as e:
            bot_response = "Не удалось обработать аудиофайл. Попробуйте снова."
            print(f"Ошибка обработки аудио: {e}")
        
        await update.message.reply_text(bot_response)
        os.remove(file_path)

# Запуск бота
def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    print("Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
