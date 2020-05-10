import json
import urllib.parse
from difflib import SequenceMatcher

import requests
from unsync import unsync

from lookup import posters


def is_similar(a, b):
    return SequenceMatcher(a=a.lower(), b=b.lower()).ratio() >= 0.5


@unsync()
def get_posters(title):
    try:
        params = urllib.parse.quote(
            json.dumps(
                {
                    "page_size": 1,
                    "page": 1,
                    "query": title,
                    "content_types": ["movie"]
                }
            )
        )
        response = requests.get(f"https://apis.justwatch.com/content/titles/en_US/popular?body={params}")
        if response.ok:
            data = response.json()["items"]
            if data and (is_similar(data[0].get("title", ""), title) or True):
                posters[title] = data[0].get("poster", "//").split("/")[-2]
            else:
                posters[title] = ""
        else:
            print(response.content)
    except Exception as e:
        print(title, e)


def get_movie_posters(title_list):
    futures = []

    for title in title_list:
        if title not in posters:
            futures.append(get_posters(title))

    for future in futures:
        future.result()

    return [dict(name=title, poster=posters.get(title, "")) for title in title_list]

