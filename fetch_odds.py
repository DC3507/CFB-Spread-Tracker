#!/usr/bin/env python3
"""
College Football spread tracker.

Pulls current CFB spreads from The Odds API and appends a snapshot to
data/snapshots.csv -- but only rows where a line actually CHANGED since the
last recorded value. That de-duping keeps the file small and makes every
row a real "movement" event.

Uses a single market (spreads) and a single region (us) so each call costs
exactly 1 credit on The Odds API's free plan.
"""

import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

API_KEY = os.environ.get("ODDS_API_KEY")
SPORT = "americanfootball_ncaaf"
REGION = "us"          # single region  -> keeps cost at 1 credit/call
MARKET = "spreads"     # single market  -> keeps cost at 1 credit/call
ODDS_FORMAT = "american"
DATA_FILE = Path("data/snapshots.csv")

FIELDS = [
    "timestamp_utc",
    "game_id",
    "commence_time",
    "home_team",
    "away_team",
    "bookmaker",
    "team",
    "spread",
    "price",
]


def fetch():
    if not API_KEY:
        sys.exit("ERROR: ODDS_API_KEY is not set. Add it as a GitHub secret.")

    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": ODDS_FORMAT,
    }
    resp = requests.get(url, params=params, timeout=30)

    if resp.status_code != 200:
        sys.exit(f"ERROR: API returned {resp.status_code}: {resp.text[:300]}")

    # These headers tell you how much of your monthly credit budget is left.
    remaining = resp.headers.get("x-requests-remaining")
    used = resp.headers.get("x-requests-used")
    print(f"Credits remaining this month: {remaining}  (used: {used})")

    return resp.json()


def flatten(games, now):
    """Turn the nested API response into flat rows, one per book+team line."""
    rows = []
    for g in games:
        for bk in g.get("bookmakers", []):
            for market in bk.get("markets", []):
                if market.get("key") != MARKET:
                    continue
                for outcome in market.get("outcomes", []):
                    rows.append({
                        "timestamp_utc": now,
                        "game_id": g["id"],
                        "commence_time": g.get("commence_time", ""),
                        "home_team": g.get("home_team", ""),
                        "away_team": g.get("away_team", ""),
                        "bookmaker": bk.get("key", ""),
                        "team": outcome.get("name", ""),
                        "spread": outcome.get("point", ""),
                        "price": outcome.get("price", ""),
                    })
    return rows


def load_last_values():
    """Return {(game_id, bookmaker, team): (spread, price)} using the most
    recent recorded value for each line, so unchanged lines can be skipped."""
    last = {}
    if not DATA_FILE.exists():
        return last
    with DATA_FILE.open(newline="") as f:
        for r in csv.DictReader(f):
            key = (r["game_id"], r["bookmaker"], r["team"])
            last[key] = (r["spread"], r["price"])
    return last


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    games = fetch()
    rows = flatten(games, now)
    if not rows:
        print("No games returned (probably off-season or between weeks). Done.")
        return

    last = load_last_values()
    changed = []
    for row in rows:
        key = (row["game_id"], row["bookmaker"], row["team"])
        current = (str(row["spread"]), str(row["price"]))
        if last.get(key) != current:
            changed.append(row)

    if not changed:
        print("No line changes since last run. Nothing written.")
        return

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    new_file = not DATA_FILE.exists()
    with DATA_FILE.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerows(changed)

    print(f"Wrote {len(changed)} changed line(s) out of {len(rows)} total.")


if __name__ == "__main__":
    main()
