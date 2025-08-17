"""_summary_
      spotify.py

      Defines functions needed to communicate with the Spotify API, including:
      - Retrieving access tokens and replacing them when they expire
      - Using that access token when making GET requests to the Spotify API
    """

from datetime import datetime, timedelta
import requests

from django.conf import settings

SPOTIFY_CLIENT_ID = settings.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET

SPOTIFY_TOKEN = None
SPOTIFY_TOKEN_EXPIRES = None


def get_spotify_token():
    """Gets a new spotify API token and sets a time that it will expire. Each new token expires in one hour.

    Returns:
        access_token: string,
        expires_at: datetime when access token expires
    """
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
        timeout=5
    )
    data = response.json()
    access_token = data["access_token"]
    expires_in = data["expires_in"]
    expires_at = datetime.now() + timedelta(seconds=expires_in)
    return access_token, expires_at


def get_cached_spotify_token():
    """Checks if a spotify token already exists or if it is expires. If it is, it fetches a new one. Sets the SPOTIFY_TOKEN global variable

    Returns:
        SPOTIFY_TOKEN: string
    """
    global SPOTIFY_TOKEN, SPOTIFY_TOKEN_EXPIRES
    if not SPOTIFY_TOKEN or datetime.now() >= SPOTIFY_TOKEN_EXPIRES:
        SPOTIFY_TOKEN, SPOTIFY_TOKEN_EXPIRES = get_spotify_token()
    return SPOTIFY_TOKEN


def spotify_get(endpoint: str, params=None):
    """Makes a GET request to the Spotify API, where the user can pass in the specific endpoint they want to access

    Args:
        endpoint (str): the endpoint the user wants to access, doesn't need a slash before it (ex. albums/1)
        params (_type_, optional): Exists so the user can pass in multiple query parameters, ex: params={"q": "beatles", "type": "artist", "limit": 5}. Defaults to None.

    Returns:
        JSON response: JSON response of the spotify endpoint that was retrieved.
    """
    token = get_cached_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/{endpoint}"
    response = requests.get(url, headers=headers, params=params, timeout=5)
    return response.json()
