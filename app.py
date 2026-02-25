"""
Python Baseball Web App
Author: Shrihan Bodapati

Simple Flask application demonstrating:
- Multi-page routing
- Template inheritance
- JSON-driven dynamic content
"""

from flask import Flask, render_template, request
import json
from pathlib import Path

app = Flask(__name__)

# ---------- Data ----------
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "players.json"


def load_players():
    """Load player data from JSON file."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- Routes ----------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/teams")
def teams():
    return render_template("teams.html")


@app.route("/players")
def players():
    players = load_players()

    # simple search feature (resume-level improvement)
    query = request.args.get("q", "").lower()

    if query:
        players = [
            p for p in players
            if query in p["name"].lower()
            or query in p["team"].lower()
        ]

    return render_template(
        "players.html",
        players=players,
        query=query
    )


# ---------- Run App ----------
if __name__ == "__main__":
    app.run(debug=True)