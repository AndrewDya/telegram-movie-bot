import httpx
from datetime import datetime


async def send_http_request(url: str) -> dict or None:
    """
    Sends an asynchronous HTTP GET request and returns the JSON response.

    :param url: The URL to send the request to.
    :return: The JSON response content as a dictionary, or None if the request fails.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        return None


async def load_photo_content(url: str) -> bytes or None:
    """
    Loads the content of a photo from the given URL.

    :param url: The URL of the photo.
    :return: The bytes content of the photo, or None if the request fails or the URL is None.
    """
    if url is None:
        return None

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.content
    return None


async def format_date(date_str: str) -> str:
    """
    Formats a date string in the format 'YYYY-MM-DD' to a human-readable format.

    :param date_str: The date string in 'YYYY-MM-DD' format.
    :return: The formatted date string like 'Day Month Yearг.',
    or "Не указана" if date_str is None.
    """
    if date_str is None:
        return "Не указана"
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    day = date_obj.day
    month = months[date_obj.month - 1]
    year = date_obj.year
    formatted_date = f"{day} {month} {year}г."
    return formatted_date


async def process_overview(overview: str) -> str:
    """
    Processes an overview text, truncating it if it exceeds a maximum length.

    :param overview: The overview text.
    :return: The processed overview text, truncated if necessary,
    or 'Нет описания' if overview is None.
    """
    if overview:
        max_length = 350
        return overview[:max_length] + (overview[max_length:] and '...')
    return 'Нет описания'


async def get_cast_genres(genres: list, cast: list, crew: list) -> tuple:
    """
    Extracts and formats information about genres, actors, and director.

    :param genres: List of genre dictionaries.
    :param cast: List of cast member dictionaries.
    :param crew: List of crew member dictionaries.
    :return: A tuple containing formatted genre names, actors list, and director's name.
    """
    genre_names = [genre["name"] for genre in genres if
                   genre.get("id") in {g["id"] for g in genres}]
    actors = [f"{actor['name']} ({actor['character']})" for actor in cast]
    director = next(
        (member["name"] for member in crew if member["job"] == "Director"),
        None)
    director = director if director is not None else "Нет информации"
    if not actors:
        actors = ["Не указаны"]

    return genre_names, actors, director


async def get_status_description(status: str) -> str:
    """
    Gets a human-readable description of a movie or series status.

    :param status: The status string.
    :return: The corresponding human-readable status description, or 'Неизвестный статус' if not found.
    """
    status_mapping = {
        "Post Production": "Пост продакшн",
        "In Production": "В производстве",
        "Returning Series": "Онлайн",
        "Planned": "Запланирован",
        "Canceled": "Отменен",
        "Pilot": "Пилотный выпуск",
        "Ended": "Завершен",
        "Released": "Выпущен",
    }
    return status_mapping.get(status, "Неизвестный статус")
