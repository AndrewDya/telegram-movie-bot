from telegram.ext import ApplicationBuilder, CommandHandler, \
    CallbackQueryHandler, MessageHandler, filters
from handlers.favorites_api import db, FavoriteMovie
from handlers.default_handlers import (handle_button_press, favorites_command,
    actors_popular_command, series_popular_command, search_command, \
    upcoming_command, top_rated_command, popular_command, help_command, \
    start_command, search_text_input)
from config import TOKEN


def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    start_handler = CommandHandler('start', start_command)
    help_handler = CommandHandler('help', help_command)
    popular_handler = CommandHandler('popular', popular_command)
    top_rated_handler = CommandHandler('top_rated', top_rated_command)
    upcoming_handler = CommandHandler('upcoming', upcoming_command)
    search_handler = CommandHandler('search', search_command)
    favorites_handler = CommandHandler('favorites', favorites_command)
    actors_popular_handler = CommandHandler('actors_popular',
                                            actors_popular_command)
    series_popular_handler = CommandHandler('series_popular',
                                            series_popular_command)

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
    app.add_handler(actors_popular_handler)
    app.add_handler(series_popular_handler)

    search_handler = MessageHandler(filters.TEXT & ~filters.COMMAND,
                                    search_text_input)
    app.add_handler(search_handler)

    db.close()

    app.run_polling()


if __name__ == '__main__':
    run_bot()
