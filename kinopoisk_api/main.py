import requests
import os
import argparse
from prettytable import PrettyTable
from collections import namedtuple

API_KEY = os.getenv("kinopoiskAPI_token")
headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}


def get_films():
    films = []
    film = None
    print("Введите названия фильмов, у которых вы хотите узнать бюджет")
    while film != ".":
        film = input()
        films.append(film)
    films.remove(".")
    return set(films)


def get_id_by_film_name(name):
    try:
        response = requests.get(
            url=f"https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword",
            params={"keyword": name},
            headers=headers,
        )
        return response.json()["films"][0]["filmId"]
    except (requests.HTTPError, requests.ConnectionError):
        print("что-то пошло не так :( Невозможно получить id фильма.")


def get_film_rating(film):
    try:
        film_id = get_id_by_film_name(film)
        response = requests.get(
            url=f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}",
            params={},
            headers=headers,
        )
        return response.json()["ratingKinopoisk"]
    except (requests.HTTPError, requests.ConnectionError):
        print("что-то пошло не так :( Невозможно получить id фильма.")


def get_film_year(film):
    try:
        film_id = get_id_by_film_name(film)
        response = requests.get(
            url=f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}",
            params={},
            headers=headers,
        )
        return response.json()["year"]
    except (requests.HTTPError, requests.ConnectionError):
        print("что-то пошло не так :( Невозможно получить id фильма.")


def get_top_films_by_budget():
    films = get_films()
    films_budget = {}
    try:
        for film in films:
            film_id = get_id_by_film_name(film)
            response = requests.get(
                url=f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}/box_office",
                params={},
                headers=headers,
            )
            data = response.json()["items"]
            for item in data:
                if item["type"] == "BUDGET":
                    budget = item["amount"]
                    films_budget[film] = budget
        sorted_tuples = sorted(
            films_budget.items(), key=lambda item: item[1], reverse=True
        )
        sorted_budget = {k: v for k, v in sorted_tuples}
        return sorted_budget
    except (requests.HTTPError, requests.ConnectionError):
        print("что-то пошло не так :( Невозможно получить информацию о бюджете фильма.")


def get_similars_films(film):
    try:
        similar_films = []
        film_id = get_id_by_film_name(film)
        response = requests.get(
            url=f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}/similars",
            params={},
            headers=headers,
        )
        film_info = namedtuple("film_info", ["name", "rating", "year"])
        for item in response.json()["items"]:
            film_name = item["nameRu"]
            similar_films.append(
                film_info(
                    name=film_name,
                    rating=get_film_rating(film_name),
                    year=get_film_year(film_name),
                )
            )
        return similar_films
    except (requests.HTTPError, requests.ConnectionError):
        print("что-то пошло не так :( Невозможно получить id фильма.")


def main():
    script_name = "API кинопоиска"
    inf = argparse.ArgumentParser(usage=f"{script_name} -t FILMS -s FILM")
    inf.add_argument(
        "-t",
        "--top",
        help="Топ фильмов по бюджету.\n",
        action="store_const",
        const=True,
    )
    inf.add_argument(
        "-s",
        "--similar",
        type=str,
        help="\nСписок похожих фильмов по названию фильма",
        nargs="+",
    )
    args = inf.parse_args()
    if args.top:
        films = get_top_films_by_budget()
        table = PrettyTable()
        table.field_names = ["Название фильма", "Бюджет($)"]
        for film in films.keys():
            table.add_row([film, films[film]])
        print(table)

    if args.similar:
        similar_films = get_similars_films(" ".join(args.similar))
        table = PrettyTable()
        table.field_names = ["Название фильма", "Рейтинг кинопоиска", "Год"]
        for film in similar_films:
            table.add_row([film.name, film.rating, film.year])
        print(table)


if __name__ == "__main__":
    main()
