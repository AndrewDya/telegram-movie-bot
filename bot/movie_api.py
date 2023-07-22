import io
import locale
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.utils import API_KEY, language, send_http_request, load_photo_content


async def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language={language}&append_to_response=credits"

    data = await send_http_request(url)
    if data:
        poster_path = data.get("poster_path")
        runtime = data.get("runtime")
        genres = data.get("genres")
        budget = data.get("budget")
        title = data.get("title")
        rating = round(data.get("vote_average"), 1)
        overview = data.get("overview")
        cast = data.get("credits", {}).get("cast", [])[:3]
        crew = data.get("credits", {}).get("crew", [])

        budget = locale.format_string("%d", budget, grouping=True) if budget else 'Неизвестен'
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        genre_names = [genre["name"] for genre in genres if genre.get("id") in {g["id"] for g in genres}]
        actors = [f"{actor['name']} ({actor['character']})" for actor in cast]
        director = next((member["name"] for member in crew if member["job"] == "Director"), None)

        max_length = 350
        sentences = re.split(r'(?<=[.!?])\s+', overview)
        while len(' '.join(sentences)) > max_length:
            sentences.pop()

        overview = ' '.join(sentences) if sentences else 'Пока нет'

        return runtime, poster_url, genre_names, actors, budget, title, \
                rating, overview, director

    return None


async def find_trailer(movie_id):
    videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
    videos_data = await send_http_request(videos_url)

    if videos_data and "results" in videos_data:
        videos_results = videos_data["results"]
        trailer = next((video for video in videos_results if
                        video.get("type") == "Trailer" and video.get("official")), None)

        # Если не найден официальный трейлер, берем первый попавшийся трейлер с размером 720 из результатов
        if not trailer:
            trailer = next((video for video in videos_results if
                            video.get("type") == "Trailer" and video.get("size") == 720), None)

        if trailer:
            trailer_key = trailer.get("key")
            trailer_url = f"https://www.youtube.com/watch?v={trailer_key}"
            return trailer_url

    return None


async def view_movie_info(movie):
    movie_id = movie.get("id")
    runtime, poster_url, genre_names, actors, budget, title, rating, \
        overview, director = await get_movie_details(movie_id)

    movie_info = f"{title}\n"
    movie_info += f"Рейтинг: {rating}\n"
    movie_info += f"Жанр: {', '.join(genre_names)}\n"
    movie_info += f"Продолжительность: {runtime} минут\n"
    movie_info += f"Бюджет: ${budget}\n"
    movie_info += f"Режиссёр: {director}\n"
    movie_info += f"Описание: {overview}\n"
    movie_info += f"Актёры: {', '.join(actors)}\n"

    # Добавляем кнопку "Смотреть трейлер"
    trailer_url = await find_trailer(movie_id)
    buttons = []
    if trailer_url:
        trailer_button = InlineKeyboardButton("Смотреть трейлер", url=trailer_url)
        buttons.append([trailer_button])

    # Добавляем кнопку "Добавить в избранное"
    add_to_favorites_button = InlineKeyboardButton("Добавить в избранное", callback_data=f"add_to_favorites_{movie_id}")
    buttons.append([add_to_favorites_button])

    keyboard = InlineKeyboardMarkup(buttons) if buttons else None

    return poster_url, movie_info, keyboard


async def send_movie_info(update, context, movies):
    for movie in movies:
        poster_url, movie_info, keyboard = await view_movie_info(movie)
        file_content = await load_photo_content(poster_url)
        if file_content:
            photo_stream = io.BytesIO(file_content)
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, photo=photo_stream,
                caption=movie_info, reply_markup=keyboard)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Ошибка при загрузке фотографии")


async def get_favorite_movie_details(update, context, movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=ru-RU"

    data = await send_http_request(url)
    if data:
        title = data.get("title")
        rating = round(data.get("vote_average"), 1)
        runtime = data.get("runtime")
        movie_info = f"{title}. Рейтинг: {rating}. Продолжительность: {runtime} минут"
        movie_data = [data]

        # Добавляем кнопки "Удалить из избранного" и "Полная информация"
        buttons_row1 = [
            InlineKeyboardButton("Просмотр",
                                 callback_data=f"view_movie_{movie_id}"),
            InlineKeyboardButton("Удалить из избранного",
                                 callback_data=f"remove_from_favorites_{movie_id}"),
        ]

        keyboard = InlineKeyboardMarkup([buttons_row1])

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=movie_info,
            reply_markup=keyboard
        )
        return movie_data


async def get_data_from_id(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=ru-RU"
    movie_data = await send_http_request(url)
    if movie_data:
        return [movie_data]


async def get_title_from_id(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=ru-RU"
    data = await send_http_request(url)
    if data:
        title = data.get("title")
        return title
