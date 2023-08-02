from peewee import SqliteDatabase, Model, CharField, IntegrityError

db = SqliteDatabase("database/movies.db")


class FavoriteMovie(Model):
    user_id = CharField()
    movie_id = CharField()

    class Meta:
        database = db


def add_to_favorites(user_id: int, movie_id: int):
    """
    Add a movie to the user's list of favorite movies.

    :param user_id: The user's identifier.
    :param movie_id: The identifier of the movie to add.
    """
    try:
        FavoriteMovie.create(user_id=user_id, movie_id=movie_id)
    except IntegrityError:
        return


def remove_from_favorites(user_id: int, movie_id: int):
    """
    Remove a movie from the user's list of favorite movies.

    :param user_id: The user's identifier.
    :param movie_id: The identifier of the movie to remove.
    """
    try:
        favorite_movie = FavoriteMovie.get(
            (FavoriteMovie.user_id == user_id) & (
                FavoriteMovie.movie_id == movie_id))
        favorite_movie.delete_instance()
    except FavoriteMovie.DoesNotExist:
        return


def get_favorite_movies(user_id: int):
    """
    Retrieve the list of movie IDs that the user has marked as favorites.

    :param user_id: The user's identifier.
    :return: A list of movie IDs marked as favorites by the user.
    """
    favorite_movie_ids = [
        favorite.movie_id for favorite in FavoriteMovie.select().where(
            FavoriteMovie.user_id == user_id)]
    return favorite_movie_ids
