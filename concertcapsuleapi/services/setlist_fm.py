import requests
from django.conf import settings

SETLIST_FM_KEY = settings.SETLIST_FM_KEY


def setlist_fm_get(endpoint: str, params=None):
    """Makes a GET request to the Setlist.FM API, where users can pass in the specific endpoint they want to access

    Args:
        endpoint (str): the endpoint the user wants to access, doesn't need a slash before it (ex. venues/1)
        params (_type_, optional): Exists so the user can pass in multiple query parameters, will be handled in the specific view making the request. Defaults to None.

    Returns:
        JSON Response: JSON response of the spotify endpoint that was retrieved.
    """
    headers = {"x-api-key": f"{SETLIST_FM_KEY}", "Accept": "application/json"}
    url = f"https://api.setlist.fm/rest/1.0/{endpoint}"
    response = requests.get(url, headers=headers, params=params, timeout=5)
    return response.json()
