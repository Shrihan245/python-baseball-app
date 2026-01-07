import json
from pathlib import Path
from flask import Flask, render_template

app = Flask(__name__)

DATA_DIR = Path(__file__).parent / "data"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/players")
def players():
    players = json.loads((DATA_DIR / "players.json").read_text(encoding="utf-8"))
    return render_template("players.html", players=players)

@app.route("/teams")
def teams():
    return render_template("teams.html")


if __name__ == "__main__":
    app.run(debug=True)