import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значения API-ключа
api_key = os.getenv('API_KEY')

TOKEN = '6187980676:AAGdLrpWboqiEpuDeQRiYC9ytp-GeiuKLnM'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="I'm a bot, please talk to me!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "Доступные команды:\n"
    response += "/help - Получить помощь по командам бота\n"
    response += "/popular - Получить список популярных фильмов\n"
    response += "/top_rated - Получить список фильмов с высоким рейтингом\n"
    response += "/upcoming - Получить список ожидаемых фильмов\n"
    response += "/search <название фильма> - Поиск фильма по названию\n"
    response += "/history - Просмотреть историю последних запросов\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    # Обработчики команд
    help_handler = CommandHandler('help', help_command)
    # Добавление обработчика команды /help перед созданием приложения
    application.add_handler(help_handler)

    # Добавление обработчиков в приложение
    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    application.run_polling()