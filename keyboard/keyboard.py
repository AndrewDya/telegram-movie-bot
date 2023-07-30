from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes
from config import API_KEY, language
from handlers.default_handlers import help_command, popular_command, \
    top_rated_command, upcoming_command, actors_popular_command, \
    series_popular_command, start_command, get_actors_by_url, get_series_by_url, \
    favorites_command, get_movies_by_url
from handlers.favorites_api import add_to_favorites, remove_from_favorites
from handlers.movie_api import get_title_from_id, get_data_from_id, \
    send_movie_info


async def handle_button_press(update, context):
    query = update.callback_query
    button_data = query.data
    global search_category

    if button_data == "help_command":
        await help_command(update, context)
    elif button_data == "search_command":
        await search_command(update, context)
    elif button_data == "favorites_command":
        await favorites_command(update, context)
    elif button_data == "popular_command":
        await popular_command(update, context, selected_count=None)
    elif button_data == "top_rated_command":
        await top_rated_command(update, context, selected_count=None)
    elif button_data == "upcoming_command":
        await upcoming_command(update, context, selected_count=None)
    elif button_data == "actors_popular_command":
        await actors_popular_command(update, context, selected_count=None)
    elif button_data == "series_popular_command":
        await series_popular_command(update, context, selected_count=None)
    elif button_data.startswith("top_"):
        selected_count = int(button_data.split("_")[1])
        await top_rated_command(update, context, selected_count)
    elif button_data.startswith("upcoming_"):
        selected_count = int(button_data.split("_")[1])
        await upcoming_command(update, context, selected_count)
    elif button_data.startswith("popular_"):
        selected_count = int(button_data.split("_")[1])
        await popular_command(update, context, selected_count)
    elif button_data.startswith("actors_popular_"):
        selected_count = int(button_data.split("_")[2])
        await actors_popular_command(update, context, selected_count)
    elif button_data.startswith("series_popular_"):
        selected_count = int(button_data.split("_")[2])
        await series_popular_command(update, context, selected_count)
    elif button_data.startswith("search_request_"):
        await search_request(update, context)
        search_category = button_data.split("_")[2]
    elif button_data == "cancel_search":
        search_category = None
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Поиск отменен.",
        )
        await start_command(update, context)
    elif button_data.startswith("add_to_favorites_"):
        movie_id = int(button_data.split("_")[3])
        add_to_favorites(update.effective_user.id, movie_id)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Фильм {await get_title_from_id(movie_id)} добавлен в избранное!")
    elif button_data.startswith("remove_from_favorites_"):
        movie_id = int(button_data.split("_")[3])
        remove_from_favorites(update.effective_user.id, movie_id)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Фильм {await get_title_from_id(movie_id)} удалён из избранного.")
        await start_command(update, context)
    elif button_data.startswith("view_movie_"):
        movie_id = int(button_data.split("_")[2])
        movie_data = await get_data_from_id(movie_id)
        await send_movie_info(update, context, movie_data)
        await start_command(update, context)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Неизвестная команда")


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global search_category
    buttons = [
        [
            InlineKeyboardButton("Фильмы 🎬",
                                 callback_data="search_request_movies"),
            InlineKeyboardButton("Актёры 🌟",
                                 callback_data="search_request_actors"),
            InlineKeyboardButton("Сериалы 📺",
                                 callback_data="search_request_series"),
        ],
        [InlineKeyboardButton("Отмена ❌", callback_data="cancel_search")],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите категорию для поиска:",
        reply_markup=keyboard,
    )

    search_category = None


async def search_request(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Введите поисковый запрос:")


async def search_text_input(update: Update, context: CallbackContext):
    global search_category

    if search_category == "movies":
        await search_movies(update, context)
    elif search_category == "actors":
        await search_actors(update, context)
    elif search_category == "series":
        await search_series(update, context)


async def search_movies(update: Update, context: CallbackContext):
    user_query = update.message.text
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={user_query}&language={language}"
    await get_movies_by_url(update, context, url, 5)


async def search_actors(update: Update, context: CallbackContext):
    user_query = update.message.text
    url = f"https://api.themoviedb.org/3/search/person?api_key={API_KEY}&query={user_query}&language={language}"
    await get_actors_by_url(update, context, url, 5)


async def search_series(update: Update, context: CallbackContext):
    user_query = update.message.text
    url = f"https://api.themoviedb.org/3/search/tv?api_key={API_KEY}&query={user_query}&language={language}"
    await get_series_by_url(update, context, url, 5)
