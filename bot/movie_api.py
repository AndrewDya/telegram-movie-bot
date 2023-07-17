import locale
import re
import httpx
from bot.utils import API_KEY, language


async def get_movie_details(movie_id):
    # URL-адрес API TMDb для получения информации о фильме
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language={language}&append_to_response=credits"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            data = response.json()

            poster_path = data.get("poster_path")
            runtime = data.get("runtime")
            genres = data.get("genres")
            budget = data.get("budget")
            title = data.get("title")
            rating = round(data.get("vote_average"), 1)
            overview = data.get("overview")
            cast = data.get("credits", {}).get("cast", [])[:5]
            crew = data.get("credits", {}).get("crew", [])

            budget = locale.format_string("%d", budget, grouping=True) \
                if budget else 'Неизвестен'
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" \
                if poster_path else None

            genre_names = [genre["name"] for genre in genres
                           if genre.get("id") in {g["id"] for g in genres}]

            actors = [f"{actor['name']} ({actor['character']})" for actor in cast]

            director = next((member["name"] for member in crew if
                             member["job"] == "Director"), None)

            sentences = re.split(r'(?<=[.!?])\s+', overview)
            overview = sentences[0] if sentences else 'Пока нет'

            # videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
            # videos_response = await client.get(videos_url)
            #
            # if videos_response.status_code == 200:
            #     videos_data = videos_response.json()
            #     videos_results = videos_data.get("results", [])
            #     trailer = next((video for video in videos_results if video.get("type") == "Trailer"
            #                     and video.get("official")), None)
            #     trailer_key = trailer.get("key") if trailer else None
            #     trailer_url = f"https://www.youtube.com/watch?v={trailer_key}" \
            #         if trailer_key else None

            return runtime, poster_url, genre_names, actors, budget, title, \
                rating, overview, director

    return None


async def view_movie_info(movie):
    movie_id = movie.get("id")
    runtime, poster_url, genre_names, actors, budget, title, rating, overview, \
        director = await get_movie_details(movie_id)

    movie_info = f"{title}\n"
    movie_info += f"Рейтинг: {rating}\n"
    movie_info += f"Жанр: {', '.join(genre_names)}\n"
    movie_info += f"Продолжительность: {runtime} минут\n"
    movie_info += f"Бюджет: ${budget}\n"
    movie_info += f"Режиссёр: {director}\n"
    movie_info += f"Описание: {overview}...\n"
    movie_info += f"Актёры: {', '.join(actors)}\n"

    return poster_url, movie_info
