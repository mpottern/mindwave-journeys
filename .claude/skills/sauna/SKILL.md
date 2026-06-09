---
name: sauna
description: Use when the user says they just got in the sauna, starts a sauna session, or types phrases like "Sauna, I just got in" / "sauna session" / "in the sauna". A hands-free wind-down ritual — playlist, reading queue, day recap, and an Oura check-in.
disable-model-invocation: false
---

## What This Skill Does

Runs the user's **in-sauna wind-down** ritual. Triggered the moment they get in
("Sauna, I just got in"). Everything is hands-free and meant to be *absorbed*,
not acted on — keep replies warm, spoken-style, and easy to skim while relaxing.

Runs four things in order. Do them in **one pass** and present as a single,
calm digest:

## Steps

### 1. Start a relaxing playlist (Spotify)

- Call the Spotify `create_playlist` tool with a prompt like:
  *"Create a calm 45-minute sauna wind-down playlist — slow ambient, soft
  neoclassical piano, and gentle downtempo to relax and sweat to."*
- **If the token is expired / re-auth error:** don't fail the whole session.
  Tell them once, briefly: *"Spotify needs a quick reconnect — Settings →
  Connectors → Spotify → Reconnect, then say 'playlist'."* Then continue with
  the rest of the ritual. (Note: playlist creation requires Spotify Premium.)

### 2. Read the `mogs` queue

The `mogs` flow forwards reading/reference/video emails to a Gmail label.
Items still carrying the **`mogs`** label are unfiled — that's the queue.

- Find the label id: call Gmail `list_labels`, locate the label named `mogs`
  (do NOT assume an id — it can change; look it up each run).
- Call Gmail `search_threads` with `query: label:<that id>` (pageSize 25).
- For each thread, give a one-line spoken digest (subject + who/what + the gist
  from the snippet). Group videos/articles/references loosely.
- **If empty:** say so plainly — *"Queue's empty, you're caught up, nothing to
  read tonight."* Don't invent items.

### 3. Day recap + tomorrow

- Call Calendar `list_events` on the primary calendar for a window covering
  **today 00:00 → day-after-tomorrow 00:00** (`orderBy: startTime`).
- **Today:** brief recap. If nothing was scheduled, say it was a clear/quiet day.
- **Tomorrow:** list each event as a compact table (time · session · with whom).
  Then add 2-3 *insights*, not just a dump:
  - Flag back-to-back stretches and any long/late sessions.
  - Flag guests whose `responseStatus` is `needsAction` (unconfirmed) — suggest
    a nudge tonight.

### 4. Oura check-in

First try to pull the numbers live: run
`python tools/oura/run.py --json` from the repo root (it reads `OURA_TOKEN`
from `tools/oura/.env` or the environment).

- **On success** (JSON with `readiness` / `sleep_score` / `hrv` / `resting_hr`):
  report them and interpret for *how to play tomorrow's load* given the calendar
  above (e.g. low readiness + a late evening session → protect the midday gap,
  hydrate, lighter morning).
- **On failure** (non-zero exit, `{"error": ...}`, or no token configured): fall
  back to asking the user to read **Readiness, Sleep score, HRV, and resting HR**
  off the app, then interpret the same way. Don't treat a missing token as a
  blocker — the manual ask is the original behavior.

Never invent values — only report what the tool returns or the user provides.

## Output Format

One message, sections in this order with light emoji headers:
🎵 Playlist · 📥 Queue · 📅 Today · 🌅 Tomorrow · 💍 Oura (the ask).
End on the Oura ask so the user knows the ball's in their court.

## Notes

- Keep it short and calm — they're relaxing, not at a desk.
- Never fabricate calendar events, emails, or Oura values.
- The Obsidian vault the `mogs` flow writes to is a **separate repo** and not
  available here — read the queue from Gmail, not from a vault checkout.
- If Spotify is down, the session still succeeds on the other three parts.
- Pairs with `/post-sauna` for the cool-down afterward.
