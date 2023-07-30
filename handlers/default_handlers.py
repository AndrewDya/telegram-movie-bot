from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackContext
from handlers.actors_api import send_actors_info
from handlers.favorites_api import get_favorite_movies, add_to_favorites, \
    remove_from_favorites
from handlers.movie_api import send_movie_info, get_favorite_movie_details, \
    get_title_from_id, get_data_from_id
from handlers.series_api import send_series_info
from config import API_KEY, language
from utils.utils import send_http_request


async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    button_data = query.data
    global search_category

    if button_data == "help_command":
        await help_command(update, context)
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
    elif button_data == "search_command":
        await search_command(update, context)
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
    elif button_data == "favorites_command":
        await favorites_command(update, context)
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


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons_row1 = [
        InlineKeyboardButton("Помощь 🤔", callback_data="help_command"),
        InlineKeyboardButton("Популярные фильмы 🎬", callback_data="popular_command"),
    ]
    buttons_row2 = [
        InlineKeyboardButton("Топ рейтинга 👍", callback_data="top_rated_command"),
        InlineKeyboardButton("Ожидаемые 🚀", callback_data="upcoming_command"),
    ]
    buttons_row3 = [
        InlineKeyboardButton("Поиск 🔍", callback_data="search_command"),
        InlineKeyboardButton("Избранное 📚", callback_data="favorites_command"),
    ]

    buttons_row4 = [
        InlineKeyboardButton("Популярные актёры 🌟", callback_data="actors_popular_command"),
        InlineKeyboardButton("Популярные сериалы 📺", callback_data="series_popular_command"),
    ]

    keyboard = InlineKeyboardMarkup([buttons_row1, buttons_row2, buttons_row3,
                                     buttons_row4])

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите команду:",
                                   reply_markup=keyboard)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "Доступные команды:\n"
    response += "Помощь - Информация по командам бота\n"
    response += "Популярные фильмы - Получить список популярных фильмов\n"
    response += "Топ рейтинга - Получить список фильмов с высоким рейтингом\n"
    response += "Ожидаемые - Получить список ожидаемых фильмов\n"
    response += "Поиск - После этой команды выберите категорию, введите" \
                "запрос и бот предоставит результаты поиска\n"
    response += "Избранное - Просмотреть фильмы добавленные в избранное\n"
    response += "Популярные актёры - Получить список популярных актёров\n"
    response += "Популярные сериалы - Получить список популярных сериалов\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    await start_command(update, context)


async def create_movie_count_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    category_names = {
        "top": "топ рейтинга фильмов",
        "popular": "популярных фильмов",
        "upcoming": "ожидаемых фильмов",
        "actors_popular": "популярных актёров",
        "series_popular": "популярных сериалов",
    }

    # Варианты числа фильмов для вывода в кнопках
    movie_counts = [1, 3, 5, 10]

    buttons = [
        InlineKeyboardButton(str(count), callback_data=f"{category}_{count}")
        for count in movie_counts
    ]

    keyboard = InlineKeyboardMarkup([buttons])
    category_name = category_names.get(category, category)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Выберите количество {category_name}, которое хотите увидеть:",
        reply_markup=keyboard
    )


async def top_rated_command(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_count=None):
    if selected_count is None:
        await create_movie_count_buttons(update, context, "top")
    else:
        url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&page=1&language={language}"
        await get_movies_by_url(update, context, url, selected_count)


async def popular_command(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_count=None):
    if selected_count is None:
        await create_movie_count_buttons(update, context, "popular")
    else:
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&page=1&language={language}"
        await get_movies_by_url(update, context, url, selected_count)


async def upcoming_command(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_count=None):
    if selected_count is None:
        await create_movie_count_buttons(update, context, "upcoming")
    else:
        url = f"https://api.themoviedb.org/3/movie/upcoming?api_key={API_KEY}&page=1&language={language}"
        await get_movies_by_url(update, context, url, selected_count)


async def actors_popular_command(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_count=None):
    if selected_count is None:
        await create_movie_count_buttons(update, context, "actors_popular")
    else:
        url = f"https://api.themoviedb.org/3/person/popular?api_key={API_KEY}&page=1&language={language}"
        await get_actors_by_url(update, context, url, selected_count)


async def series_popular_command(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_count=None):
    if selected_count is None:
        await create_movie_count_buttons(update, context, "series_popular")
    else:
        url = f"https://api.themoviedb.org/3/tv/popular?api_key={API_KEY}&language={language}"
        await get_series_by_url(update, context, url, selected_count)


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


async def favorites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    favorite_movie_ids = get_favorite_movies(user_id)

    if not favorite_movie_ids:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Список избранных фильмов пуст.")
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"Список избранных фильмов {len(favorite_movie_ids)}:")

    for movie_id in favorite_movie_ids:
        await get_favorite_movie_details(update, context, movie_id)


async def get_movies_by_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, selected_count: int,):
    data = await send_http_request(url)
    if data and "results" in data:
        movies = data["results"][:selected_count]
        await send_movie_info(update, context, movies)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Ошибка при получении данных о фильмах")
    await start_command(update, context)


async def get_actors_by_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, selected_count: int):
    data = await send_http_request(url)
    if data and "results" in data:
        actors = data["results"][:selected_count]
        await send_actors_info(update, context, actors)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ошибка при получении данных об актёрах"
        )
    await start_command(update, context)


async def get_series_by_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, selected_count: int):
    data = await send_http_request(url)
    if data and "results" in data:
        series_list = data["results"][:selected_count]
        await send_series_info(update, context, series_list)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ошибка при получении данных о сериалах"
        )
    await start_command(update, context)
