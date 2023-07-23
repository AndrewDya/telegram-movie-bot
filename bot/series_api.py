import io
import re
from datetime import datetime
from bot.utils import API_KEY, send_http_request, load_photo_content, language

import io
from datetime import datetime
from bot.utils import API_KEY, send_http_request


async def get_series_details(series_id):
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

        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        rating = "Ещё не выставлен" if rating == 0 else rating

        genre_names = [genre["name"] for genre in genres if
                       genre.get("id") in {g["id"] for g in genres}]
        actors = [f"{actor['name']} ({actor['character']})" for actor in cast]
        director = next(
            (member["name"] for member in crew if member["job"] == "Director"),
            None)

        director = director if director is not None else "Нет информации"

        if overview:
            max_length = 350
            overview = overview[:max_length] + (
                        overview[max_length:] and '...')
        else:
            overview = 'Пока нет'

        date_obj = datetime.strptime(first_air_date, "%Y-%m-%d")
        months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]
        day = date_obj.day
        month = months[date_obj.month - 1]
        year = date_obj.year

        new_status = {
            "Post Production": "Постпродакшн",
            "In Production": "В производстве",
            "Returning Series": "Онлайн",
            "Planned": "Запланирован",
            "Canceled": "Отменен",
            "Pilot": "Пилотный выпуск",
            "Ended": "Завершен"
        }.get(status, "Неизвестный статус")

        formatted_date = f"{day} {month} {year}г."

        return poster_url, genre_names, actors, title, \
            rating, overview, director, formatted_date, new_status

    return None


async def view_series_info(series):
    # Извлекаем информацию о сериале из переданного словаря
    series_id = series.get("id")
    poster_url, genre_names, actors, title, rating, overview, director, \
        formatted_date, new_status = await get_series_details(series_id)

    # Формируем текстовое сообщение с информацией о сериале
    series_info = f"{title}\n"
    series_info += f"Рейтинг: {rating}\n"
    series_info += f"Жанр: {', '.join(genre_names)}\n"
    series_info += f"Статус: {new_status}\n"
    series_info += f"Дата выхода первого эпизода: {formatted_date}\n"
    series_info += f"Режиссёр: {director}\n"
    series_info += f"Описание: {overview}\n"
    series_info += f"Актёры: {', '.join(actors)}\n"

    # Добавляем кнопку "Добавить в избранное" (также, как в предыдущем коде)

    # Формируем клавиатуру для сообщения, если есть кнопки

    # Отправляем сообщение пользователю с информацией о сериале и клавиатурой (если есть)

    return poster_url, series_info


async def send_series_info(update, context, series_list):
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
