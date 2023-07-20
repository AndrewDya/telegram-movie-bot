import sqlite3
import os


def get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_relative_path = "movies.db"
    db_path = os.path.join(current_dir, db_relative_path)

    return db_path


def search_movies(query):
    # Подключение к базе данных SQLite
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Выполнение запроса к базе данных с поиском в нижнем регистре, ограничив результаты до 3
    query_lower = query.lower()
    cursor.execute("SELECT id FROM movies WHERE lower(title) LIKE ? LIMIT 2", ('%' + query_lower + '%',))
    results_lower = cursor.fetchall()

    # Выполнение запроса к базе данных с поиском по подстроке с заглавной буквой, ограничив результаты до 3
    query_capitalized = query.capitalize()
    cursor.execute("SELECT id FROM movies WHERE title LIKE ? LIMIT 2", ('%' + query_capitalized + '%',))
    results_capitalized = cursor.fetchall()

    # Закрытие соединения с базой данных
    conn.close()

    # Извлекаем только ID из результатов запросов
    movie_ids_lower = [result[0] for result in results_lower]
    movie_ids_capitalized = [result[0] for result in results_capitalized]

    # Комбинируем результаты из обоих запросов, чтобы получить уникальные ID фильмов
    movie_id = list(set(movie_ids_lower + movie_ids_capitalized))

    return movie_id
