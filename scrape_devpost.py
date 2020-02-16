from itertools import count
import requests
import json

search_url = "https://devpost.com/software/search"

with open("projects.txt", "a", encoding="utf-8") as f:
    for i in count():
        params = {"query": "has:video", "page": i}
        r = requests.get(search_url, params=params)
        json = r.json()

        for project in r.json()["software"]:
            title = project["name"]
            desc = project["tagline"]
            f.write(f"{title}\n{desc}\n\n")
            f.flush()
