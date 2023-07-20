from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.movie_api import send_movie_info
from bot.utils import API_KEY, language, send_http_request


async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    button_data = query.data

    if button_data == "help_command":
        await help_command(update, context)
    elif button_data == "popular_command":
        await popular_command(update, context, selected_count=None)
    elif button_data.startswith("popular_"):
        selected_count = int(button_data.split("_")[1])
        await popular_command(update, context, selected_count)
    elif button_data == "top_rated_command":
        await top_rated_command(update, context, selected_count=None)
    elif button_data.startswith("top_"):
        selected_count = int(button_data.split("_")[1])
        await top_rated_command(update, context, selected_count)
    elif button_data == "upcoming_command":
        await upcoming_command(update, context, selected_count=None)
    elif button_data.startswith("upcoming_"):
        selected_count = int(button_data.split("_")[1])
        await upcoming_command(update, context, selected_count)
    elif button_data == "search_command":
        await search_command(update, context)
    elif button_data == "favorites_command":
        await favorites_command(update, context)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Неизвестная команда")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создание кнопок команд с визуальными стилями
    buttons_row1 = [
        InlineKeyboardButton("Помощь 🤔", callback_data="help_command"),
        InlineKeyboardButton("Популярные фильмы 🎬", callback_data="popular_command"),
    ]
    buttons_row2 = [
        InlineKeyboardButton("Топ рейтинга 👍", callback_data="top_rated_command"),
        InlineKeyboardButton("Ожидаемые 🚀", callback_data="upcoming_command"),
    ]
    buttons_row3 = [
        InlineKeyboardButton("Поиск фильма 🔍", callback_data="search_command"),
        InlineKeyboardButton("Избранное 📚", callback_data="favorites_command"),
    ]

    # Создание разметки с кнопками
    keyboard = InlineKeyboardMarkup([buttons_row1, buttons_row2, buttons_row3])

    # Отправка сообщения с кнопками
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите команду:",
                                   reply_markup=keyboard)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "Доступные команды:\n"
    response += "Помощь - Информация по командам бота\n"
    response += "Популярные фильмы - Получить список популярных фильмов\n"
    response += "Топ рейтинга - Получить список фильмов с высоким рейтингом\n"
    response += "Ожидаемые - Получить список ожидаемых фильмов\n"
    response += "Поиск фильма - После этой команды введите название фильма " \
                "и бот предоставит результаты поиска\n"
    response += "Избранное - Просмотреть фильмы добавленные в избранное\n"

    # Отправка сообщения с текстом команд и кнопками
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    # Вызов функции start_command для отображения кнопок
    await start_command(update, context)


async def create_movie_count_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    # Варианты числа фильмов для вывода в кнопках
    movie_counts = [1, 3, 5, 10]

    # Создание кнопок с вариантами числа фильмов
    buttons = [
        InlineKeyboardButton(str(count), callback_data=f"{category}_{count}")
        for count in movie_counts
    ]
    keyboard = InlineKeyboardMarkup([buttons])

    # Отправка сообщения с вопросом о выборе числа фильмов
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Выберите количество {category} фильмов, которое хотите увидеть:",
        reply_markup=keyboard
    )


async def get_movies_by_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, selected_count: int,):
    data = await send_http_request(url)
    if data and "results" in data:
        movies = data["results"][:selected_count]
        await send_movie_info(update, context, movies)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Ошибка при получении данных о фильмах")
    await start_command(update, context)


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


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите название фильма для поиска:")
    #
    # # Получаем ответ пользователя
    # user_response = await context.bot.get_updates()


async def favorites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
