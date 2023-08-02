import io
from typing import Optional, List, Dict, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from utils.utils import send_http_request, load_photo_content, \
    format_date, process_overview
from config import API_KEY, language


async def get_actor_details(actor_id: int) -> Optional[Tuple[str, str, str, str]]:
    """
    Fetches details about an actor using their ID from TheMovieDB API.

    :param actor_id: The ID of the actor.
    :return: A tuple containing actor name, photo URL, formatted birthday, and overview.
             Returns None if data is not available.
    """
    url = f"https://api.themoviedb.org/3/person/{actor_id}?api_key={API_KEY}"
    data = await send_http_request(url)

    if data:
        actor_name = data.get("name")
        profile_path = data.get("profile_path")
        birthday = data.get("birthday")
        biography = data.get("biography")

        formatted_birthday = await format_date(birthday)
        photo_url = f"https://image.tmdb.org/t/p/w500{profile_path}" \
            if profile_path else None
        overview = await process_overview(biography)

        return actor_name, photo_url, formatted_birthday, overview

    return None


async def get_movies_list(actor_id: int) -> Optional[List[Dict[str, str]]]:
    """
    Retrieves a list of movies associated with an actor's ID.

    :param actor_id: The ID of the actor.
    :return: A list of dictionaries containing movie IDs and titles.
             Returns None if no data is available.
    """
    actor_name = await get_name_from_id(actor_id)
    if not actor_name:
        return None

    url = f"https://api.themoviedb.org/3/search/person?api_key={API_KEY}&query={actor_name}&language={language}"
    data = await send_http_request(url)

    if data and data["results"]:
        actor_info = data["results"][0]
        known_for = actor_info.get("known_for", [])
        movies = [{"id": movie.get("id"), "title": movie.get("title")}
                  for movie in known_for if movie.get("title")]
        return movies

    return None


async def view_actor_info(actor: Dict) -> Optional[Tuple[str, str, InlineKeyboardMarkup]]:
    """
    Generates a formatted actor information string and an inline keyboard for associated movies.

    :param actor: Dictionary containing actor information.
    :return: A tuple containing photo URL, actor information string, and an inline keyboard.
             Returns None if data is not available.
    """
    actor_id = actor.get("id")
    actor_name, photo_url, formatted_birthday, overview = \
        await get_actor_details(actor_id)
    movies = await get_movies_list(actor_id)

    actor_info = f"{actor_name}\n"
    actor_info += f"Дата рождения: {formatted_birthday}\n"
    actor_info += f"Биография: {overview}\n"
    actor_info += f"Фильмография: {', '.join(movie['title'] for movie in movies if movie)}\n"

    buttons = []
    if movies:
        first_two_movies = movies[:2]
        for movie in first_two_movies:
            movie_id = movie["id"]
            movie_title = movie["title"]
            button = InlineKeyboardButton(movie_title,
                                          callback_data=f"view_movie_{movie_id}")
            buttons.append([button])

        keyboard = InlineKeyboardMarkup(buttons)

        return photo_url, actor_info, keyboard


async def send_actors_info(update: Update, context: CallbackContext, actors: List[Dict]):
    """
    Sends formatted actor information along with photos and an inline keyboard to the user.

    :param update: The received update object.
    :param context: The context for the callback.
    :param actors: List of dictionaries containing actor information.
    """
    for actor in actors:
        photo_url, actor_info, keyboard = await view_actor_info(actor)
        file_content = await load_photo_content(photo_url)
        if file_content:
            photo_stream = io.BytesIO(file_content)
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, photo=photo_stream,
                caption=actor_info, reply_markup=keyboard
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=actor_info
            )


async def get_name_from_id(actor_id: int) -> Optional[str]:
    """
    Retrieves the name of an actor using their ID from TheMovieDB API.

    :param actor_id: The ID of the actor.
    :return: The name of the actor, or None if data is not available.
    """
    url = f"https://api.themoviedb.org/3/person/{actor_id}?api_key={API_KEY}"
    data = await send_http_request(url)
    if data:
        name = data.get("name")
        return name
