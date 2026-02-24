import requests


BASE_URL = "https://www.caliente.mx/sports/api"


def get_events():

    url = f"{BASE_URL}/sportsbook/events"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return []

    return r.json()
