"""
Baseball & Me — Flask Web Application
Author: Shrihan Bodapati

A data-driven, multi-page Flask app showcasing baseball players and teams.

Demonstrates:
  - Multi-page routing with Flask
  - Template inheritance with Jinja2
  - JSON-driven dynamic content
  - Server-side search with query params
  - Clean separation of data, logic, and presentation
"""

from flask import Flask, render_template, request
import json
from pathlib import Path
from mlb_api import get_standings

app = Flask(__name__)

# ─── Paths ────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent
PLAYERS_FILE = BASE_DIR / "data" / "players.json"
TEAMS_FILE   = BASE_DIR / "data" / "teams.json"


# ─── Data Helpers ─────────────────────────────────────────

def load_players() -> list[dict]:
    """Load all player records from JSON."""
    with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_teams() -> list[dict]:
    """Load all team records from JSON."""
    with open(TEAMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def search_players(players: list[dict], query: str) -> list[dict]:
    """
    Filter players by a case-insensitive query string.
    Matches against player name or team name.
    """
    q = query.lower().strip()
    return [
        p for p in players
        if q in p["name"].lower() or q in p["team"].lower()
    ]


# ─── Routes ───────────────────────────────────────────────

@app.route("/")
def home():
    players = load_players()
    teams   = load_teams()
    return render_template(
        "index.html",
        active_page="home",
        total_players=len(players),
        total_teams=len(teams),
    )


@app.route("/players")
def players():
    all_players = load_players()
    query       = request.args.get("q", "").strip()

    filtered = search_players(all_players, query) if query else all_players

    return render_template(
        "players.html",
        active_page="players",
        players=filtered,
        query=query,
    )


@app.route("/teams")
def teams():
    all_teams = load_teams()
    return render_template(
        "teams.html",
        active_page="teams",
        teams=all_teams,
    )

@app.route("/standings")
def standings():
    divisions = get_standings()
    return render_template(
        "standings.html",
        active_page="standings",
        divisions=divisions,
    )


@app.route("/about")
def about():
    players = load_players()
    teams   = load_teams()
    return render_template(
        "about.html",
        active_page="about",
        total_players=len(players),
        total_teams=len(teams),
    )


# ─── Entry Point ──────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)