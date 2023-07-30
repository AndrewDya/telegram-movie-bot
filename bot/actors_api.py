import io
from bot.utils import send_http_request, API_KEY, load_photo_content, \
    format_date, process_overview, language


async def get_actor_details(actor_id):
    url = f"https://api.themoviedb.org/3/person/{actor_id}?api_key={API_KEY}"

    data = await send_http_request(url)
    if data:
        actor_name = data.get("name")
        profile_path = data.get("profile_path")
        birthday = data.get("birthday")
        biography = data.get("biography")

        formatted_birthday = await format_date(birthday)
        photo_url = f"https://image.tmdb.org/t/p/w500{profile_path}" if profile_path else None
        overview = await process_overview(biography)

        return actor_name, photo_url, formatted_birthday, overview

    return None


async def get_movies_list(actor_id):
    actor_name = await get_name_from_id(actor_id)
    if not actor_name:
        return None

    url = f"https://api.themoviedb.org/3/search/person?api_key={API_KEY}&query={actor_name}&language={language}"
    data = await send_http_request(url)

    if data and data["results"]:
        actor_info = data["results"][0]
        known_for = actor_info.get("known_for", [])
        movie_names = [movie.get("title") for movie in known_for]

        return movie_names

    return None


async def view_actor_info(actor):
    actor_id = actor.get("id")
    actor_name, photo_url, formatted_birthday, overview = await get_actor_details(actor_id)
    movie_names = await get_movies_list(actor_id)

    actor_info = f"{actor_name}\n"
    actor_info += f"Дата рождения: {formatted_birthday}\n"
    actor_info += f"Биография: {overview}\n"
    actor_info += f"Фильмография: {', '.join(movie for movie in movie_names if movie)}\n"

    return photo_url, actor_info


async def send_actors_info(update, context, actors):
    for actor in actors:
        photo_url, actor_info = await view_actor_info(actor)
        file_content = await load_photo_content(photo_url)
        if file_content:
            photo_stream = io.BytesIO(file_content)
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, photo=photo_stream,
                caption=actor_info
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=actor_info
            )


async def get_name_from_id(actor_id):
    url = f"https://api.themoviedb.org/3/person/{actor_id}?api_key={API_KEY}"
    data = await send_http_request(url)
    if data:
        name = data.get("name")
        return name
