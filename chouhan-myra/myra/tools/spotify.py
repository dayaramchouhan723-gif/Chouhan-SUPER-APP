"""Open Spotify search results in the user's default browser."""

from __future__ import annotations

import webbrowser
from urllib.parse import quote


def search_spotify(query: str) -> str:
    if not query.strip():
        return "Add a song, artist, or playlist after /spotify."
    url = f"https://open.spotify.com/search/{quote(query.strip())}"
    if not webbrowser.open(url):
        return "Could not open Spotify in the default browser."
    return f"Opened Spotify search for: {query.strip()}"
