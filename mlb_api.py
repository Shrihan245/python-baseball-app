"""
MLB Stats API client — a wrapper around MLB's free, public, official
stats API (https://statsapi.mlb.com). No API key needed, no auth.

Each function does ONE thing: call an endpoint, reshape the JSON into
something simple for templates to loop over, and fail gracefully
(return empty/None) rather than crash the app if the API is down.
"""

import time
import requests

STANDINGS_URL = "https://statsapi.mlb.com/api/v1/standings"
TEAMS_URL = "https://statsapi.mlb.com/api/v1/teams"
PEOPLE_URL = "https://statsapi.mlb.com/api/v1/people"
PEOPLE_SEARCH_URL = "https://statsapi.mlb.com/api/v1/people/search"

# American League = 103, National League = 104 — fixed IDs MLB uses internally
LEAGUE_IDS = "103,104"

# The STANDINGS endpoint only returns division {id, link}, not a name —
# these numeric IDs are fixed MLB constants, so we map them ourselves.
# (The TEAMS endpoint, used elsewhere below, DOES include the name directly.)
DIVISION_NAMES = {
    200: "American League West",
    201: "American League East",
    202: "American League Central",
    203: "National League West",
    204: "National League East",
    205: "National League Central",
}

_standings_cache = {"data": None, "fetched_at": 0}
STANDINGS_CACHE_TTL_SECONDS = 300  # standings change often; refresh every 5 min

_teams_cache = {"data": None, "fetched_at": 0}
TEAMS_CACHE_TTL_SECONDS = 3600  # teams/divisions basically never change mid-season


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
    Returns [] if the API call fails for any reason.
    """
    now = time.time()
    if _standings_cache["data"] is not None and (now - _standings_cache["fetched_at"]) < STANDINGS_CACHE_TTL_SECONDS:
        return _standings_cache["data"]

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

    _standings_cache["data"] = divisions
    _standings_cache["fetched_at"] = now
    return divisions


def get_all_teams():
    """
    Fetch all 30 active MLB teams, grouped by division.

    Returns a list shaped like:
        [
          {"division_name": "American League East",
           "teams": [{"id": 147, "name": "New York Yankees", "abbreviation": "NYY",
                       "league_name": "American League", "venue_name": "Yankee Stadium",
                       "first_year": "1901"}, ...]},
          ...
        ]
    Returns [] if the API call fails for any reason.
    """
    now = time.time()
    if _teams_cache["data"] is not None and (now - _teams_cache["fetched_at"]) < TEAMS_CACHE_TTL_SECONDS:
        return _teams_cache["data"]

    try:
        response = requests.get(TEAMS_URL, params={"sportId": 1}, timeout=5)
        response.raise_for_status()
        raw = response.json()
    except requests.RequestException:
        return []

    by_division = {}
    for team in raw.get("teams", []):
        division_name = team.get("division", {}).get("name", "Unknown Division")
        by_division.setdefault(division_name, []).append({
            "id": team.get("id"),
            "name": team.get("name", "Unknown"),
            "abbreviation": team.get("abbreviation", ""),
            "league_name": team.get("league", {}).get("name", ""),
            "venue_name": team.get("venue", {}).get("name", "—"),
            "first_year": team.get("firstYearOfPlay", "—"),
        })

    divisions = [
        {"division_name": name, "teams": sorted(teams, key=lambda t: t["name"])}
        for name, teams in sorted(by_division.items())
    ]

    _teams_cache["data"] = divisions
    _teams_cache["fetched_at"] = now
    return divisions


def get_team_by_id(team_id):
    """Find a single team's info from the cached full team list. Returns None if not found."""
    for division in get_all_teams():
        for team in division["teams"]:
            if team["id"] == team_id:
                return {**team, "division_name": division["division_name"]}
    return None


def get_team_roster(team_id):
    """
    Fetch a team's current active roster.

    Returns a list shaped like:
        [{"person_id": 660271, "full_name": "Shohei Ohtani",
          "jersey_number": "17", "position_name": "Designated Hitter",
          "position_abbr": "DH"}, ...]
    Returns [] if the API call fails for any reason.
    """
    try:
        response = requests.get(
            f"{TEAMS_URL}/{team_id}/roster",
            params={"rosterType": "active"},
            timeout=5,
        )
        response.raise_for_status()
        raw = response.json()
    except requests.RequestException:
        return []

    roster = []
    for entry in raw.get("roster", []):
        person = entry.get("person", {})
        position = entry.get("position", {})
        roster.append({
            "person_id": person.get("id"),
            "full_name": person.get("fullName", "Unknown"),
            "jersey_number": entry.get("jerseyNumber", "—"),
            "position_name": position.get("name", "—"),
            "position_abbr": position.get("abbreviation", "—"),
        })
    roster.sort(key=lambda p: p["full_name"])
    return roster


def search_players(query):
    """
    Search live MLB players by name.

    Returns a list shaped like:
        [{"person_id": 660271, "full_name": "Shohei Ohtani",
          "team_name": "Los Angeles Dodgers", "position_name": "Designated Hitter"}, ...]
    Returns [] if the query is too short or the API call fails.
    """
    if not query or len(query.strip()) < 2:
        return []

    try:
        response = requests.get(PEOPLE_SEARCH_URL, params={"names": query}, timeout=5)
        response.raise_for_status()
        raw = response.json()
    except requests.RequestException:
        return []

    results = []
    for person in raw.get("people", []):
        results.append({
            "person_id": person.get("id"),
            "full_name": person.get("fullName", "Unknown"),
            "team_name": person.get("currentTeam", {}).get("name", "Free Agent"),
            "position_name": person.get("primaryPosition", {}).get("name", "—"),
        })
    return results


def get_player_profile(person_id):
    """
    Fetch a player's bio info. Returns a dict, or None if not found.
    """
    try:
        response = requests.get(f"{PEOPLE_URL}/{person_id}", timeout=5)
        response.raise_for_status()
        raw = response.json()
    except requests.RequestException:
        return None

    people = raw.get("people", [])
    if not people:
        return None
    person = people[0]

    return {
        "person_id": person.get("id"),
        "full_name": person.get("fullName", "Unknown"),
        "position_name": person.get("primaryPosition", {}).get("name", "—"),
        "position_type": person.get("primaryPosition", {}).get("type", ""),
        "team_name": person.get("currentTeam", {}).get("name", "Free Agent"),
        "jersey_number": person.get("primaryNumber", "—"),
        "birth_date": person.get("birthDate", "—"),
        "birth_city": person.get("birthCity", ""),
        "birth_country": person.get("birthCountry", ""),
        "height": person.get("height", "—"),
        "weight": person.get("weight", "—"),
        "bat_side": person.get("batSide", {}).get("description", "—"),
        "pitch_hand": person.get("pitchHand", {}).get("description", "—"),
    }


def get_player_season_stats(person_id, is_pitcher=False):
    """
    Fetch a player's current-season stats (hitting or pitching).
    Returns a dict of stat values, or None if no stats exist yet.
    """
    group = "pitching" if is_pitcher else "hitting"
    try:
        response = requests.get(
            f"{PEOPLE_URL}/{person_id}/stats",
            params={"stats": "season", "group": group},
            timeout=5,
        )
        response.raise_for_status()
        raw = response.json()
    except requests.RequestException:
        return None

    stats_list = raw.get("stats", [])
    if not stats_list or not stats_list[0].get("splits"):
        return None

    stat = stats_list[0]["splits"][0].get("stat", {})

    if is_pitcher:
        return {
            "era": stat.get("era", "—"),
            "wins": stat.get("wins", 0),
            "losses": stat.get("losses", 0),
            "strikeouts": stat.get("strikeOuts", 0),
            "innings_pitched": stat.get("inningsPitched", "—"),
        }
    else:
        return {
            "avg": stat.get("avg", "—"),
            "home_runs": stat.get("homeRuns", 0),
            "rbi": stat.get("rbi", 0),
            "ops": stat.get("ops", "—"),
        }