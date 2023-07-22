import sqlite3
from database.database import get_db_path


def add_to_favorites(user_id, movie_id):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Проверяем, существует ли комбинация user_id и movie_id в таблице
    cursor.execute('SELECT COUNT(*) FROM favorites WHERE user_id = ? AND movie_id = ?', (user_id, movie_id))
    count = cursor.fetchone()[0]

    if count == 0:
        # Если комбинации ещё нет, добавляем новую запись
        cursor.execute(
            'INSERT INTO favorites (user_id, movie_id) VALUES (?, ?)',
            (user_id, movie_id))
        conn.commit()
    else:
        # Если комбинация уже существует, просто возвращаемся, не выполняя вставку
        return

    conn.close()


def remove_from_favorites(user_id, movie_id):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM favorites WHERE user_id = ? AND movie_id = ?', (user_id, movie_id))

    conn.commit()
    conn.close()


def get_favorite_movies(user_id):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT movie_id FROM favorites WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()

    favorite_movie_ids = [result[0] for result in results]

    conn.close()

    return favorite_movie_ids


