from peewee import SqliteDatabase, Model, CharField, IntegrityError

# Определяем модель для таблицы favorites
db = SqliteDatabase("database/movies.db")


class FavoriteMovie(Model):
    user_id = CharField()
    movie_id = CharField()

    class Meta:
        database = db


# Функция для добавления фильма в избранное
def add_to_favorites(user_id, movie_id):
    try:
        FavoriteMovie.create(user_id=user_id, movie_id=movie_id)
    except IntegrityError:
        # Если комбинация user_id и movie_id существует, просто возвращаемся
        return


# Функция для удаления фильма из избранного
def remove_from_favorites(user_id, movie_id):
    try:
        favorite_movie = FavoriteMovie.get(
            (FavoriteMovie.user_id == user_id) & (
                FavoriteMovie.movie_id == movie_id))
        favorite_movie.delete_instance()
    except FavoriteMovie.DoesNotExist:
        # Если комбинация user_id и movie_id не найдена, просто возвращаемся
        return


# Функция для получения списка избранных фильмов пользователя
def get_favorite_movies(user_id):
    favorite_movie_ids = [
        favorite.movie_id for favorite in FavoriteMovie.select().where(
            FavoriteMovie.user_id == user_id)]
    return favorite_movie_ids
