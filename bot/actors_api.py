import io
import re
from datetime import datetime
from bot.utils import send_http_request, API_KEY, load_photo_content


async def get_actor_details(actor_id):
    url = f"https://api.themoviedb.org/3/person/{actor_id}?api_key={API_KEY}"

    data = await send_http_request(url)
    if data:
        actor_name = data.get("name")
        profile_path = data.get("profile_path")
        birthday = data.get("birthday")
        biography = data.get("biography")

        # Формируем дату рождения в нужном формате (день месяц год)
        date_obj = datetime.strptime(birthday, "%Y-%m-%d")
        months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]
        day = date_obj.day
        month = months[date_obj.month - 1]
        year = date_obj.year

        formatted_birthday = f"{day} {month} {year}г."

        photo_url = f"https://image.tmdb.org/t/p/w500{profile_path}" if profile_path else None

        max_length = 350
        sentences = re.split(r'(?<=[.!?])\s+', biography)
        while len(' '.join(sentences)) > max_length:
            sentences.pop()

        overview = ' '.join(sentences) if sentences else 'Пока нет информации'

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

