import io
import httpx
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.movie_api import view_movie_info
from bot.utils import API_KEY, language


async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    button_data = query.data

    if button_data == "help_command":
        await help_command(update, context)
    elif button_data == "popular_command":
        await popular_command(update, context)
    elif button_data == "top_rated_command":
        await top_rated_command(update, context)
    elif button_data == "upcoming_command":
        await upcoming_command(update, context)
    elif button_data == "search_command":
        await search_command(update, context)
    elif button_data == "history_command":
        await history_command(update, context)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создание кнопок команд
    buttons_row1 = [
        InlineKeyboardButton("Помощь", callback_data="help_command"),
        InlineKeyboardButton("Популярные фильмы", callback_data="popular_command"),
    ]
    buttons_row2 = [
        InlineKeyboardButton("Топ рейтинга", callback_data="top_rated_command"),
        InlineKeyboardButton("Ожидаемые", callback_data="upcoming_command"),
    ]
    buttons_row3 = [
        InlineKeyboardButton("Поиск фильма", callback_data="search_command"),
        InlineKeyboardButton("История", callback_data="history_command"),
    ]

    # Создание разметки с кнопками
    keyboard = InlineKeyboardMarkup([buttons_row1, buttons_row2, buttons_row3])

    # Отправка сообщения с кнопками
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите команду:",
                                   reply_markup=keyboard)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "Доступные команды:\n"
    response += "/help - Получить помощь по командам бота\n"
    response += "/popular - Получить список популярных фильмов\n"
    response += "/top_rated - Получить список фильмов с высоким рейтингом\n"
    response += "/upcoming - Получить список ожидаемых фильмов\n"
    response += "/search <название фильма> - Поиск фильма по названию\n"
    response += "/history - Просмотреть историю последних запросов\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


async def popular_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&page=1&language={language}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            data = response.json()

            if "results" in data:
                movies = data["results"][:5]  #TODO поменять 5, добавить ввод от пользователя

                for movie in movies:
                    poster_url, movie_info = await view_movie_info(movie)

                    photo_data = requests.get(poster_url).content
                    photo_stream = io.BytesIO(photo_data)
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id, photo=photo_stream,
                        caption=movie_info)

        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Ошибка при получении данных о популярных фильмах")


async def top_rated_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&page=1&language={language}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            data = response.json()

            if "results" in data:
                movies = data["results"][:5]  #TODO поменять 5, добавить ввод от пользователя

                for movie in movies:
                    poster_url, movie_info = await view_movie_info(movie)

                    # Загружаем содержимое файла по URL-адресу
                    file_response = await client.get(poster_url)
                    if file_response.status_code == 200:
                        file_content = file_response.content
                        # Отправляем содержимое файла и информацию о фильме в чат
                        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=file_content, caption=movie_info)

        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Ошибка при получении данных о фильмах с высоким рейтингом")


async def upcoming_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.themoviedb.org/3/movie/upcoming?api_key={API_KEY}&page=1&language={language}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            data = response.json()

            if "results" in data:
                movies = data["results"][:5]  #TODO поменять 5, добавить ввод от пользователя

                for movie in movies:
                    poster_url, movie_info = await view_movie_info(movie)

                    # Загружаем содержимое файла по URL-адресу
                    file_response = await client.get(poster_url)
                    if file_response.status_code == 200:
                        file_content = file_response.content
                        # Отправляем содержимое файла и информацию о фильме в чат
                        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=file_content, caption=movie_info)

        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Ошибка при получении данных о ожидаемых фильмах")


async def search_command():
    pass


async def history_command():
    pass
