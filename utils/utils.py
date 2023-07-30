import os
import httpx
from datetime import datetime


# Вспомогательная функция для отправки HTTP-запроса
async def send_http_request(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        return None


# Вспомогательная функция для загрузки фотографии и получения ее содержимого
async def load_photo_content(url):
    if url is None:
        return None

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.content
    return None


# Функция для форматирования даты
async def format_date(date_str):
    if date_str is None:
        return "Не указана"  # Или верните другое значение, если требуется
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


# Функция для обработки описания
async def process_overview(overview):
    if overview:
        max_length = 350
        return overview[:max_length] + (overview[max_length:] and '...')
    return 'Нет описания'


# Функция для обработки жанров, работников
async def get_cast_genres(genres, cast, crew):
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


# Функция для обработки статуса
async def get_status_description(status):
    status_mapping = {
        "Post Production": "Постпродакшн",
        "In Production": "В производстве",
        "Returning Series": "Онлайн",
        "Planned": "Запланирован",
        "Canceled": "Отменен",
        "Pilot": "Пилотный выпуск",
        "Ended": "Завершен",
        "Released": "Выпущен",
    }
    return status_mapping.get(status, "Неизвестный статус")


# Получаем абсолютный путь, указывая отн-ный путь, начиная с папки проекта
def get_db_path(file):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    db_path = os.path.join(parent_dir, file)

    return db_path
