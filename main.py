import os
import io
import re
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


async def get_movie_details(movie_id):
    # URL-адрес API TMDb для получения информации о фильме
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language={language}&append_to_response=credits"

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
            cast = data.get("credits", {}).get("cast", [])[:5]
            crew = data.get("credits", {}).get("crew", [])

            budget = locale.format_string("%d", budget, grouping=True) \
                if budget else 'Неизвестен'
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" \
                if poster_path else None

            genre_names = [genre["name"] for genre in genres
                           if genre.get("id") in {g["id"] for g in genres}]

            actors = [f"{actor['name']} ({actor['character']})" for actor in cast]

            director = next((member["name"] for member in crew if
                             member["job"] == "Director"), None)

            sentences = re.split(r'(?<=[.!?])\s+', overview)
            overview = sentences[0] if sentences else 'Пока нет'

            # videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
            # videos_response = await client.get(videos_url)
            #
            # if videos_response.status_code == 200:
            #     videos_data = videos_response.json()
            #     videos_results = videos_data.get("results", [])
            #     trailer = next((video for video in videos_results if video.get("type") == "Trailer"
            #                     and video.get("official")), None)
            #     trailer_key = trailer.get("key") if trailer else None
            #     trailer_url = f"https://www.youtube.com/watch?v={trailer_key}" \
            #         if trailer_key else None

            return runtime, poster_url, genre_names, actors, budget, title, \
                rating, overview, director

    return None


async def view_movie_info(movie):
    movie_id = movie.get("id")
    runtime, poster_url, genre_names, actors, budget, title, rating, overview, \
        director = await get_movie_details(movie_id)

    movie_info = f"{title}\n"
    movie_info += f"Рейтинг: {rating}\n"
    movie_info += f"Жанр: {', '.join(genre_names)}\n"
    movie_info += f"Продолжительность: {runtime} минут\n"
    movie_info += f"Бюджет: ${budget}\n"
    movie_info += f"Режиссёр: {director}\n"
    movie_info += f"Описание: {overview}...\n"
    movie_info += f"Актёры: {', '.join(actors)}\n"

    return poster_url, movie_info


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
