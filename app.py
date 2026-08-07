"""
Baseball & Me — Flask Web Application
Author: Shrihan Bodapati

A data-driven, multi-page Flask app showcasing live MLB teams,
rosters, players, and standings via MLB's public Stats API.
"""

from flask import Flask, render_template, request, abort
import mlb_api

app = Flask(__name__)


# ─── Routes ───────────────────────────────────────────────

@app.route("/")
def home():
    divisions = mlb_api.get_all_teams()
    total_teams = sum(len(d["teams"]) for d in divisions)
    return render_template(
        "index.html",
        active_page="home",
        total_players=780,  # approx. active MLB roster spots (30 teams x 26-man roster)
        total_teams=total_teams,
    )


@app.route("/players")
def players():
    query = request.args.get("q", "").strip()
    results = mlb_api.search_players(query) if query else []
    return render_template(
        "players.html",
        active_page="players",
        players=results,
        query=query,
    )


@app.route("/players/<int:person_id>")
def player_detail(person_id):
    profile = mlb_api.get_player_profile(person_id)
    if not profile:
        abort(404)

    is_pitcher = profile["position_type"] == "Pitcher"
    stats = mlb_api.get_player_season_stats(person_id, is_pitcher=is_pitcher)

    return render_template(
        "player_detail.html",
        active_page="players",
        player=profile,
        stats=stats,
        is_pitcher=is_pitcher,
    )


@app.route("/teams")
def teams():
    divisions = mlb_api.get_all_teams()
    return render_template(
        "teams.html",
        active_page="teams",
        divisions=divisions,
    )


@app.route("/teams/<int:team_id>")
def team_detail(team_id):
    team = mlb_api.get_team_by_id(team_id)
    if not team:
        abort(404)

    roster = mlb_api.get_team_roster(team_id)

    return render_template(
        "team_detail.html",
        active_page="teams",
        team=team,
        roster=roster,
    )


@app.route("/standings")
def standings():
    divisions = mlb_api.get_standings()
    return render_template(
        "standings.html",
        active_page="standings",
        divisions=divisions,
    )


@app.route("/about")
def about():
    divisions = mlb_api.get_all_teams()
    total_teams = sum(len(d["teams"]) for d in divisions)
    return render_template(
        "about.html",
        active_page="about",
        total_players=780,
        total_teams=total_teams,
    )


# ─── Entry Point ──────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)