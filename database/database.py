import sqlite3
import httpx
from bot.utils import API_KEY, language


async def populate_movies_database():
    # Создаём подключение к базе данных
    conn = sqlite3.connect('movies.db')

    # Создаём курсор для выполнения SQL-запросов
    cursor = conn.cursor()

    # Максимальное количество страниц для запроса
    max_pages = 39133 #500

    for page in range(1, 500):
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language={language}&page={page}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if "results" in data:
                    movies = data["results"]

                    # Вставляем данные о фильмах в базу данных
                    for movie in movies:
                        movie_id = movie.get("id")
                        title = movie.get("title")
                        rating = movie.get("vote_average")
                        release_date = movie.get("release_date")
                        runtime = movie.get("runtime", None)

                        # Выполняем SQL-запрос для вставки данных о фильме
                        cursor.execute(
                            "INSERT INTO movies (id, title, rating, release_date, runtime) VALUES (?, ?, ?, ?, ? )",
                            (movie_id, title, rating, release_date, runtime)
                        )

    # Фиксируем изменения и закрываем подключение к базе данных
    conn.commit()
    conn.close()


# Запускаем функцию заполнения базы данных
import asyncio
asyncio.run(populate_movies_database())
