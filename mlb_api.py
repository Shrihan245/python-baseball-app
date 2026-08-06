"""
MLB Stats API client — a tiny wrapper around MLB's free, public,
official stats API (https://statsapi.mlb.com). No API key needed.

This module does ONE thing on purpose: fetch standings and reshape
the JSON into something simple for templates to loop over. Keeping
it single-purpose makes it easy to explain: "this calls a REST API
and reshapes the response into a clean list of dicts."
"""

import time
import requests

STANDINGS_URL = "https://statsapi.mlb.com/api/v1/standings"

# American League = 103, National League = 104 — fixed IDs MLB uses internally
LEAGUE_IDS = "103,104"

# The standings endpoint only returns division {id, link}, not a name —
# these numeric IDs are fixed MLB constants, so we map them ourselves.
DIVISION_NAMES = {
    200: "American League West",
    201: "American League East",
    202: "American League Central",
    203: "National League West",
    204: "National League East",
    205: "National League Central",
}

# Simple in-memory cache so we don't hit the live API on every page load.
# Standings only change a handful of times a day, so 5 minutes is plenty fresh.
_cache = {"data": None, "fetched_at": 0}
CACHE_TTL_SECONDS = 300


def get_standings():
    """
    Fetch current MLB standings, grouped by division.

    Returns a list shaped like:
        [
          {
            "division_name": "American League East",
            "teams": [
              {"name": "New York Yankees", "wins": 90, "losses": 70,
               "pct": ".563", "games_back": "-", "rank": "1", "streak": "W3"},
              ...
            ]
          },
          ...
        ]

    Returns an empty list if the API call fails for any reason — the
    caller decides how to handle that (we show a friendly message
    instead of crashing the page).
    """
    now = time.time()
    if _cache["data"] is not None and (now - _cache["fetched_at"]) < CACHE_TTL_SECONDS:
        return _cache["data"]

    try:
        response = requests.get(
            STANDINGS_URL,
            params={"leagueId": LEAGUE_IDS, "standingsTypes": "regularSeason"},
            timeout=5,
        )
        response.raise_for_status()
        raw = response.json()
    except requests.RequestException:
        return []

    divisions = []
    for record in raw.get("records", []):
        division_id = record.get("division", {}).get("id")
        division_name = DIVISION_NAMES.get(division_id, "Unknown Division")
        teams = []
        for team_record in record.get("teamRecords", []):
            teams.append({
                "name": team_record.get("team", {}).get("name", "Unknown"),
                "wins": team_record.get("wins", 0),
                "losses": team_record.get("losses", 0),
                "pct": team_record.get("winningPercentage", "—"),
                "games_back": team_record.get("gamesBack", "—"),
                "rank": team_record.get("divisionRank", "—"),
                "streak": team_record.get("streak", {}).get("streakCode", "—"),
            })
        teams.sort(key=lambda t: int(t["rank"]) if str(t["rank"]).isdigit() else 99)
        divisions.append({"division_name": division_name, "teams": teams})

    _cache["data"] = divisions
    _cache["fetched_at"] = now
    return divisions