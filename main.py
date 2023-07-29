from bot.handlers import (start_command, help_command, popular_command, \
    top_rated_command, upcoming_command, search_command, favorites_command, \
    handle_button_press, actors_popular_command, series_popular_command,
                          search_text_input)
from bot.utils import TOKEN
from telegram.ext import ApplicationBuilder, CommandHandler, \
    CallbackQueryHandler, MessageHandler, filters

from database.favorites import db, FavoriteMovie

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    start_handler = CommandHandler('start', start_command)
    help_handler = CommandHandler('help', help_command)
    popular_handler = CommandHandler('popular', popular_command)
    top_rated_handler = CommandHandler('top_rated', top_rated_command)
    upcoming_handler = CommandHandler('upcoming', upcoming_command)
    search_handler = CommandHandler('search', search_command)
    favorites_handler = CommandHandler('favorites', favorites_command)
    actors_popular_handler = CommandHandler('actors_popular', actors_popular_command)
    series_popular_handler = CommandHandler('series_popular', series_popular_command)

    # Обработчик callback query
    app.add_handler(CallbackQueryHandler(handle_button_press))

    db.connect()
    db.create_tables([FavoriteMovie], safe=True)

    app.add_handler(start_handler)
    app.add_handler(help_handler)
    app.add_handler(popular_handler)
    app.add_handler(top_rated_handler)
    app.add_handler(upcoming_handler)
    app.add_handler(search_handler)
    app.add_handler(favorites_handler)

    search_handler = MessageHandler(filters.TEXT & ~filters.COMMAND,
                                    search_text_input)

    app.add_handler(search_handler)

    app.run_polling()
    db.close()
