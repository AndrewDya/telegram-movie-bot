import os
import io
import logging
import httpx
import locale
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, \
    CallbackQueryHandler

# Загрузка переменных окружения из файла .env
load_dotenv()
API_KEY = os.getenv('API_KEY')
TOKEN = os.getenv('TOKEN')
language = 'ru-RU'

locale.setlocale(locale.LC_ALL, '')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

commands = ["help_command", "popular_command", "top_rated_command",
            "upcoming_command", "search_command", "history_command"]


async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    button_data = query.data

    if button_data == commands[0]:
        await help_command(update, context)
    elif button_data == commands[1]:
        await popular_command(update, context)
    elif button_data == commands[2]:
        await top_rated_command(update, context)
    elif button_data == commands[3]:
        await upcoming_command(update, context)
    elif button_data == commands[4]:
        await search_command(update, context)
    elif button_data == commands[5]:
        await history_command(update, context)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создание кнопок команд
    buttons_row1 = [
        InlineKeyboardButton("Помощь", callback_data=commands[0]),
        InlineKeyboardButton("Популярные фильмы", callback_data=commands[1]),
    ]
    buttons_row2 = [
        InlineKeyboardButton("Топ рейтинга", callback_data=commands[2]),
        InlineKeyboardButton("Ожидаемые", callback_data=commands[3]),
    ]
    buttons_row3 = [
        InlineKeyboardButton("Поиск фильма", callback_data=commands[4]),
        InlineKeyboardButton("История", callback_data=commands[5]),
    ]

    # Создание разметки с кнопками
    keyboard = InlineKeyboardMarkup([buttons_row1, buttons_row2, buttons_row3])

    # Отправка сообщения с кнопками
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите команду:",
                                   reply_markup=keyboard)


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


async def get_movie_details(movie_id):
    # URL-адрес API TMDb для получения информации о фильме
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language={language}&append_to_response=credits,videos"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            data = response.json()

            poster_path = data.get("poster_path")
            runtime = data.get("runtime")
            genres = data.get("genres")
            budget = data.get("budget")
            title = data.get("title")
            rating = round(data.get("vote_average"), 1)
            overview = data.get("overview")

            if budget:
                budget = locale.format_string("%d", budget, grouping=True)
            else:
                budget = 'Неизвестен'

            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            else:
                poster_url = None

            if genres:
                genres_dict = {genre["id"]: genre["name"] for genre in genres}
                genre_names = [genres_dict.get(genre["id"]) for genre in genres if genre["id"] in genres_dict]
            else:
                genre_names = []

            cast = data.get("credits", {}).get("cast", [])[:5]
            actors = [f"{actor['name']} ({actor['character']})" for actor in cast]

            crew = data.get("credits", {}).get("crew", [])
            director = next((member["name"] for member in crew if
                             member["job"] == "Director"), None)

            if overview:
                overview = data.get("overview")
            else:
                overview = 'Пока нет'

            return runtime, poster_url, genre_names, actors, budget, title, rating, overview, director

    return None


async def view_movie_info(movie):
    movie_id = movie.get("id")
    runtime, poster_url, genre_names, actors, budget, title, rating, overview, director = await get_movie_details(movie_id)

    movie_info = f"{title}\n"
    movie_info += f"Рейтинг: {rating}\n"
    movie_info += f"Жанр: {', '.join(genre_names)}\n"
    movie_info += f"Продолжительность: {runtime} минут\n"
    movie_info += f"Бюджет: ${budget}\n"
    movie_info += f"Режиссёр: {director}\n"
    movie_info += f"Описание: {overview}\n"
    movie_info += f"Актёры: {', '.join(actors)}"

    return poster_url, movie_info


async def popular_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&page=1&language={language}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            data = response.json()

            if "results" in data:
                movies = data["results"][:5]  # Получаем информацию о 10 популярных фильмах

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
                movies = data["results"][:5]  # Получаем информацию о 10 фильмах с высоким рейтингом

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
                movies = data["results"][:5]  # Получаем информацию о 10 ожидаемых фильмах

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
