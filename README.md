# CFB Spread Tracker

Automatically records how College Football point spreads move through the week,
across US sportsbooks, and writes a plain-English summary of the biggest moves.

**How it works in one breath:** GitHub runs a small script on a schedule for
free. Each run grabs the current spreads, saves *only the lines that changed*,
and rebuilds `MOVEMENT.md` so you can read what moved without opening a
spreadsheet. You set it up once; after that it runs itself.

---

## 🛠️ SETUP — do this once (~15 minutes)

Do them in order. Don't skip ahead. After each step there's a "✅ Done when…"
so you know you can move on.

- [ ] **1. Get your free API key.**
  Go to **the-odds-api.com** → click **Get API Key** → enter your email.
  ✅ Done when you have a long code (looks like `a1b2c3...`). Keep the tab open.

- [ ] **2. Make a new GitHub repo.**
  Go to **github.com/new**. Name it `cfb-spread-tracker`. Choose **Public**
  (public repos get unlimited free runs). Click **Create repository**.
  ✅ Done when you're looking at your new empty repo. *(Make a GitHub account
  first if you don't have one.)*

- [ ] **3. Add the project files.**
  Download the files you were given. In your repo:
  **Add file ▸ Upload files** and drag in `fetch_odds.py`, `report.py`,
  `requirements.txt`, and `README.md`. Click **Commit changes**.
  Then the workflow needs to sit in a folder: **Add file ▸ Create new file**,
  and in the name box type exactly `.github/workflows/track.yml` (the slashes
  create the folders). Open the `track.yml` you downloaded, copy everything,
  paste it in, **Commit changes**.
  ✅ Done when you see all 5 files, including `.github/workflows/track.yml`.

- [ ] **4. Save your API key as a secret.**
  In the repo: **Settings ▸ Secrets and variables ▸ Actions ▸
  New repository secret**. Name it **exactly** `ODDS_API_KEY`. Paste your key.
  **Add secret**.
  ✅ Done when `ODDS_API_KEY` shows in the secrets list. (You'll never see the
  value again — that's normal.)

- [ ] **5. Turn on Actions.**
  Click the **Actions** tab. If it asks, click the green
  **"I understand my workflows, enable them"** button.
  ✅ Done when you see a workflow named **Track CFB Spreads**.

- [ ] **6. Do a test run.**
  Click **Track CFB Spreads ▸ Run workflow ▸ Run workflow**. Wait ~1 minute
  and refresh.
  ✅ Done when the run has a green ✓.

- [ ] **7. Confirm data landed.**
  Open `data/snapshots.csv` and `MOVEMENT.md` in your repo.
  ✅ Done when they have content. **That's it — it now runs on its own.**

---

## ▶️ HOW TO USE IT — ongoing (zero effort)

You don't have to *do* anything. It runs on the schedule by itself. To check on it:

- **See what moved:** open **`MOVEMENT.md`** in your repo. Biggest opening→now
  moves are at the top. This file rewrites itself after every run.
- **See raw history:** open `data/snapshots.csv`. Every row is one line change,
  time-stamped in UTC.
- **Look up one team (optional, needs Python on your computer):**
  download the repo, then run `python report.py "Alabama"` to print that team's
  full line history.
- **Run it right now on demand:** Actions tab ▸ Track CFB Spreads ▸ Run workflow.

---

## 🎛️ Change how often it checks

Open `.github/workflows/track.yml` and edit the two `cron:` lines near the top
(there are comments right there). More runs = more detail but more credits.

Rough budget: the free plan gives **500 credits/month**, and this uses **1 credit
per run** (because it asks for one market + one region). The default schedule
uses ~155/month, so you've got lots of room to add runs on Saturday if you want.

---

## 🩹 If something breaks

| What you see | Fix |
|---|---|
| Red ✗ + "ODDS_API_KEY is not set" | The secret name must be exactly `ODDS_API_KEY` (Step 4). |
| Red ✗ + "API returned 401/429" | You're out of monthly credits, or the key is wrong. Wait for the 1st of the month, or slow the schedule. |
| No new data for a while | Normal between game weeks, or off-season. Also: GitHub pauses schedules after 60 days of no repo activity — just hit **Run workflow** once to wake it up. |
| Scheduled run is a few minutes late | Normal. GitHub's free scheduler isn't exact to the minute. |

---

_This tool records and summarizes public betting lines. It is not betting advice._
