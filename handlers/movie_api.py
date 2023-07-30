import io
import locale
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.utils import send_http_request, load_photo_content, \
    process_overview, format_date, get_cast_genres, get_status_description
from config import API_KEY, language


async def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language={language}&append_to_response=credits"
    data = await send_http_request(url)

    if data:
        poster_path = data.get("poster_path")
        runtime = data.get("runtime")
        genres = data.get("genres")
        budget = data.get("budget")
        revenue = data.get("revenue")
        title = data.get("title")
        status = data.get("status")
        rating = round(data.get("vote_average"), 1)
        overview = data.get("overview")
        release_date = data.get("release_date")
        cast = data.get("credits", {}).get("cast", [])[:3]
        crew = data.get("credits", {}).get("crew", [])

        budget = locale.format_string("%d", budget, grouping=True) \
            if budget else 'Неизвестен'
        revenue = locale.format_string("%d", revenue, grouping=True) \
            if revenue else 'Неизвестны'
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" \
            if poster_path else None
        rating = "Ещё не выставлен" if rating == 0 else rating

        genre_names, actors, director = await get_cast_genres(genres, cast,crew)
        overview = await process_overview(overview)
        formatted_date = await format_date(release_date)
        new_status = await get_status_description(status)

        return runtime, poster_url, genre_names, actors, budget, title, \
                rating, overview, director, revenue, formatted_date, new_status

    return None


async def find_trailer(movie_id):
    videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
    videos_data = await send_http_request(videos_url)

    if videos_data and "results" in videos_data:
        videos_results = videos_data["results"]

        russian_trailer = next((video for video in videos_results if
                                video.get("type") == "Trailer" and
                                video.get("iso_639_1") == "ru"), None)

        if russian_trailer:
            trailer_key = russian_trailer.get("key")
            trailer_url = f"https://www.youtube.com/watch?v={trailer_key}"
            return trailer_url

        official_trailer = next((video for video in videos_results if
                                 video.get("type") == "Trailer" and
                                 video.get("official")), None)

        if official_trailer:
            trailer_key = official_trailer.get("key")
            trailer_url = f"https://www.youtube.com/watch?v={trailer_key}"
            return trailer_url

        any_trailer = next((video for video in videos_results if
                            video.get("type") == "Trailer" and
                            video.get("size") == 720), None)

        if any_trailer:
            trailer_key = any_trailer.get("key")
            trailer_url = f"https://www.youtube.com/watch?v={trailer_key}"
            return trailer_url

    return None


async def view_movie_info(movie):
    movie_id = movie.get("id")
    runtime, poster_url, genre_names, actors, budget, title, rating, \
        overview, director, revenue, formatted_date, new_status\
        = await get_movie_details(movie_id)

    movie_info = f"{title}\n"
    movie_info += f"Рейтинг: {rating}\n"
    movie_info += f"Жанр: {', '.join(genre_names)}\n"
    movie_info += f"Продолжительность: {runtime} минут\n"
    movie_info += f"Бюджет: ${budget}\n"
    movie_info += f"Сборы: ${revenue}\n"
    movie_info += f"Статус фильма: {new_status}\n"
    movie_info += f"Дата выхода: {formatted_date}\n"
    movie_info += f"Режиссёр: {director}\n"
    movie_info += f"Описание: {overview}\n"
    movie_info += f"Актёры: {', '.join(actors)}\n"

    # Добавляем кнопки "Смотреть трейлер" и "Добавить в избранное"
    trailer_url = await find_trailer(movie_id)
    buttons = []
    if trailer_url:
        trailer_button = InlineKeyboardButton("Смотреть трейлер", url=trailer_url)
        buttons.append([trailer_button])

    add_to_favorites_button = InlineKeyboardButton("Добавить в избранное",
                                                   callback_data=f"add_to_favorites_{movie_id}")
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
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language={language}"

    data = await send_http_request(url)
    if data:
        title = data.get("title")
        rating = round(data.get("vote_average"), 1)
        runtime = data.get("runtime")
        movie_info = f"{title}. Рейтинг: {rating}. Продолжительность: {runtime} минут"
        movie_data = [data]

        # Добавляем кнопки "Удалить из избранного" и "Просмотр"
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
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language={language}"
    movie_data = await send_http_request(url)
    if movie_data:
        return [movie_data]


async def get_title_from_id(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language={language}"
    data = await send_http_request(url)
    if data:
        title = data.get("title")
        return title
