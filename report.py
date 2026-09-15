#!/usr/bin/env python3
"""
Build MOVEMENT.md -- a readable summary of the biggest line moves so far.
This runs automatically in GitHub Actions after each fetch, so you can just
open MOVEMENT.md in your repo and read it. No spreadsheet required.

You can ALSO run it locally to look up one team's full history:
    python report.py "Alabama"
"""

import csv
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

DATA_FILE = Path("data/snapshots.csv")
REPORT_FILE = Path("MOVEMENT.md")


def load():
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open(newline="") as f:
        return list(csv.DictReader(f))


def to_float(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return None


def build_moves(rows):
    """For each (game, book, team) line, compare its first recorded value to
    its latest, and return the ones that moved, biggest first."""
    series = defaultdict(list)
    for r in rows:
        s = to_float(r["spread"])
        if s is None:
            continue
        key = (r["away_team"], r["home_team"], r["bookmaker"], r["team"])
        series[key].append((r["timestamp_utc"], s))

    moves = []
    for (away, home, book, team), pts in series.items():
        pts.sort()
        opened, current = pts[0][1], pts[-1][1]
        if opened != current:
            moves.append((abs(current - opened), away, home, book, team, opened, current))

    moves.sort(reverse=True)
    return moves


def write_report(rows):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    moves = build_moves(rows)

    out = [
        "# CFB Spread Movement",
        "",
        f"_Last updated: {now}_  ",
        f"_{len(rows)} line snapshots recorded so far._",
        "",
    ]

    if not moves:
        out.append("No line movement recorded yet. Check back after a few runs.")
    else:
        out.append("## Biggest moves (opening line -> latest)")
        out.append("")
        out.append("| Move | Matchup | Book | Team | Open | Now |")
        out.append("|-----:|---------|------|------|-----:|----:|")
        for delta, away, home, book, team, opened, current in moves[:30]:
            out.append(
                f"| {delta:.1f} | {away} @ {home} | {book} | {team} "
                f"| {opened:+.1f} | {current:+.1f} |"
            )

    REPORT_FILE.write_text("\n".join(out) + "\n")
    print(f"Wrote {REPORT_FILE} ({len(moves)} lines moved).")


def team_history(rows, query):
    q = query.lower()
    hits = [
        r for r in rows
        if q in r["team"].lower()
        or q in r["home_team"].lower()
        or q in r["away_team"].lower()
    ]
    if not hits:
        sys.exit(f"No lines found for '{query}'.")

    hits.sort(key=lambda r: (r["bookmaker"], r["team"], r["timestamp_utc"]))
    print(f"\nLine history containing '{query}':\n")
    for r in hits:
        print(
            f"{r['timestamp_utc']}  {r['bookmaker']:14}  {r['team'][:22]:22}  "
            f"spread {str(r['spread']):>6}  price {str(r['price']):>5}"
        )


def main():
    rows = load()
    if len(sys.argv) > 1:
        if not rows:
            sys.exit("No data yet. Let the tracker run first.")
        team_history(rows, sys.argv[1])
    else:
        write_report(rows)


if __name__ == "__main__":
    main()
