# ⚾ Baseball & Me

A data-driven, multi-page web application built with **Python** and **Flask** — combining a genuine love of baseball with hands-on full-stack development and a live integration with MLB's official Stats API.

> **Live demo:** [python-baseball-app.onrender.com](https://python-baseball-app.onrender.com)

![App Preview](baseball-preview.png)

---

## What It Does

| Page | Description |
|------|-------------|
| **Home** | Landing page with a scoreboard ticker, live team/roster counts, and feature cards |
| **Standings** | Live division standings for all 30 MLB teams — wins, losses, win %, games back, streak |
| **Teams** | All 30 MLB teams grouped by division, live from the API. Click any team to see its current active roster |
| **Players** | Live player search by name — no need to know a player's team, just search "Judge" or "Ohtani" directly |
| **Player Detail** | Individual player page with live current-season stats (batting or pitching, detected automatically) plus bio info — birthdate, hometown, height/weight, bats/throws |
| **About** | Project breakdown — tech stack, learnings, and what's next |

---

## Tech Stack

- **Backend** — Python 3, Flask, Jinja2
- **Frontend** — Vanilla HTML5, CSS3 (custom variables, grid, animations)
- **Data** — [MLB Stats API](https://statsapi.mlb.com) (official, free, no API key required) — fully live, no static files
- **Dev Tools** — Git, GitHub, pip, requests

No JavaScript frameworks. No CSS libraries. No stored data — everything is fetched live. Built from scratch.

---

## Features

- **Live external API integration** — every page (except About) pulls real, current MLB data on request
- **Smart caching** — standings cached 5 minutes, team/division lists cached 1 hour, since that data changes far less often than live game state; player stats are always fetched fresh
- **Graceful degradation** — if the MLB API is slow or down, pages show a friendly "temporarily unavailable" message instead of crashing
- **On-demand fetching** — player season stats are only requested when someone actually views that specific player, not pre-loaded for all ~750 active players
- **Automatic stat-type detection** — a player's position determines whether batting or pitching stats are shown, no manual tagging needed
- **Multi-page routing** — clean URL structure via Flask's `@app.route`, including dynamic routes like `/teams/<id>` and `/players/<id>`
- **Template inheritance** — shared layout with Jinja2 `{% extends %}` and `{% block %}`
- **Live server-side search** — searches MLB's actual player database via `/people/search`, not a local list
- **Responsive design** — CSS Grid layout adapts to mobile, tablet, and desktop
- **Active nav state** — current page highlighted via `active_page` context variable

---

## Project Structure