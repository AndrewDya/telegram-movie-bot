from bot.handlers import start_command, help_command, popular_command, \
    top_rated_command, upcoming_command, search_command, history_command, \
    handle_button_press
from bot.utils import TOKEN
from telegram.ext import ApplicationBuilder, CommandHandler, \
    CallbackQueryHandler


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    start_handler = CommandHandler('start', start_command)
    help_handler = CommandHandler('help', help_command)
    popular_handler = CommandHandler('popular', popular_command)
    top_rated_handler = CommandHandler('top_rated', top_rated_command)
    upcoming_handler = CommandHandler('upcoming', upcoming_command)
    search_handler = CommandHandler('search', search_command)
    history_handler = CommandHandler('history', history_command)

    # Обработчик callback query
    app.add_handler(CallbackQueryHandler(handle_button_press))

    app.add_handler(start_handler)
    app.add_handler(help_handler)
    app.add_handler(popular_handler)
    app.add_handler(top_rated_handler)
    app.add_handler(upcoming_handler)
    app.add_handler(search_handler)
    app.add_handler(history_handler)

    app.run_polling()
