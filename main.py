import os
import logging
import httpx
import locale
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, \
    CallbackQueryHandler

# Загрузка переменных окружения из файла .env и получение значения API-ключа
load_dotenv()
api_key = os.getenv('API_KEY')

TOKEN = '6187980676:AAGdLrpWboqiEpuDeQRiYC9ytp-GeiuKLnM'
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
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=ru-RU"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            data = response.json()

            poster_path = data.get("poster_path")
            runtime = data.get("runtime")
            genres = data.get("genres")
            budget = data.get("budget")
            title = data.get("title")
            rating = data.get("vote_average")
            overview = data.get("overview")

            budget = locale.format_string("%d", budget, grouping=True)

            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            else:
                poster_url = None

            if genres:
                genres_dict = {genre["id"]: genre["name"] for genre in genres}
                genre_names = [genres_dict.get(genre["id"]) for genre in genres if genre["id"] in genres_dict]
            else:
                genre_names = []

            # Получаем информацию об актёрах
            credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}"
            credits_response = await client.get(credits_url)

            if credits_response.status_code == 200:
                credits_data = credits_response.json()
                cast = credits_data.get("cast", [])[:5]  # Ограничиваем список первыми 5 актёрами
                actors = [actor["name"] for actor in cast]
            else:
                actors = []

            return runtime, poster_url, genre_names, actors, budget, title, rating, overview

    return None


async def view_movie_info(movie):
    movie_id = movie.get("id")
    runtime, poster_url, genre_names, actors, budget, title, rating, overview = await get_movie_details(movie_id)

    movie_info = f"{title}\n"
    movie_info += f"Рейтинг: {rating}\n"
    movie_info += f"Жанр: {', '.join(genre_names)}\n"
    movie_info += f"Продолжительность: {runtime} минут\n"
    movie_info += f"Бюджет: ${budget}\n"
    movie_info += f"Обзор: {overview}\n"
    movie_info += f"Актёры: {', '.join(actors)}"

    return poster_url, movie_info


async def popular_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=ru-RU&page=1"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            data = response.json()

            if "results" in data:
                movies = data["results"][:1]  # Работает только с 1. Почему?

                for movie in movies:
                    poster_url, movie_info = await view_movie_info(movie)

                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=poster_url, caption=movie_info)

        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Ошибка при получении данных о популярных фильмах")


async def top_rated_command():
    pass


async def upcoming_command():
    pass


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
