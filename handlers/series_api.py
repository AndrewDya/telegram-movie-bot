import io
from typing import List, Dict, Tuple, Optional
from telegram import Update
from telegram.ext import CallbackContext
from utils.utils import load_photo_content, process_overview, \
    format_date, get_cast_genres, get_status_description, send_http_request
from config import API_KEY, language


async def get_series_details(series_id: int) -> Optional[Tuple]:
    """
    Fetches details about a TV series using its ID from TheMovieDB API.

    :param series_id: The ID of the TV series.
    :return: A tuple containing poster URL, genre names, actor names, title, rating, overview, director,
             formatted date, and new status. Returns None if data is not available.
    """
    url = f"https://api.themoviedb.org/3/tv/{series_id}?api_key={API_KEY}&language={language}&append_to_response=credits"

    data = await send_http_request(url)
    if data:
        poster_path = data.get("poster_path")
        genres = data.get("genres")
        title = data.get("name")
        status = data.get("status")
        rating = round(data.get("vote_average"), 1)
        overview = data.get("overview")
        first_air_date = data.get("first_air_date")
        cast = data.get("credits", {}).get("cast", [])[:3]
        crew = data.get("credits", {}).get("crew", [])

        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" \
            if poster_path else None
        rating = "Ещё не выставлен" if rating == 0 else rating

        genre_names, actors, director = await get_cast_genres(genres, cast, crew)
        overview = await process_overview(overview)
        formatted_date = await format_date(first_air_date)
        new_status = await get_status_description(status)

        return poster_url, genre_names, actors, title, \
            rating, overview, director, formatted_date, new_status

    return None


async def view_series_info(series: Dict) -> Tuple:
    """
    Generates a formatted series information string.

    :param series: Dictionary containing series information.
    :return: A tuple containing poster URL and series information string.
    """
    series_id = series.get("id")
    poster_url, genre_names, actors, title, rating, overview, director, \
        formatted_date, new_status = await get_series_details(series_id)

    series_info = f"{title}\n"
    series_info += f"Рейтинг: {rating}\n"
    series_info += f"Жанр: {', '.join(genre_names)}\n"
    series_info += f"Статус: {new_status}\n"
    series_info += f"Дата выхода первого эпизода: {formatted_date}\n"
    series_info += f"Режиссёр: {director}\n"
    series_info += f"Описание: {overview}\n"
    series_info += f"Актёры: {', '.join(actors)}\n"

    return poster_url, series_info


async def send_series_info(update: Update, context: CallbackContext, series_list: List[Dict]):
    """
    Sends formatted series information along with poster images to the user.

    :param update: The received update object.
    :param context: The context for the callback.
    :param series_list: List of dictionaries containing series information.
    """
    for series in series_list:
        poster_url, series_info = await view_series_info(series)
        file_content = await load_photo_content(poster_url)
        if file_content:
            photo_stream = io.BytesIO(file_content)
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, photo=photo_stream,
                caption=series_info)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Ошибка при загрузке фотографии")
