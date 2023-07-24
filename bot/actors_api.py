import io
from bot.utils import send_http_request, API_KEY, load_photo_content, \
    format_date, process_overview


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


async def view_actor_info(actor):
    actor_id = actor.get("id")
    actor_name, photo_url, formatted_birthday, overview = await get_actor_details(actor_id)

    actor_info = f"{actor_name}\n"
    actor_info += f"Дата рождения: {formatted_birthday}\n"
    actor_info += f"Биография: {overview}\n"

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

