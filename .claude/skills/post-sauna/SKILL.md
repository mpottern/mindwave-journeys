---
name: post-sauna
description: Use when the user gets out of the sauna or starts cooling down — phrases like "post sauna", "just got out", "out of the sauna", "cooling down", "sauna's done". A recovery + capture + wind-down-to-sleep ritual.
disable-model-invocation: false
---

## What This Skill Does

Runs the user's **post-sauna cool-down** ritual — the bookend to `/sauna`.
Goal: rehydrate, capture anything that surfaced during the heat, and ease toward
rest. Still hands-free and calm. Keep it short.

## Steps

### 1. Recovery nudge

Open with a brief, warm recovery prompt:
- **Hydrate** (water + electrolytes if they sweated hard) and cool down gradually.
- One gentle line, not a lecture.

### 2. Capture what came up

Saunas surface ideas, tasks, and reflections. Ask: *"Anything come up in there
worth keeping — an idea, a to-do, or just a thought to journal?"*

- If they share something, route it the way the `mogs` flow would categorize it
  (task / idea / reference / journal). Offer to **save it** via the available
  notes tools — PyNotes (`create_note`) or Notion (`notion-create-pages`) —
  tagging it so it lands in the right bucket. Confirm where it went.
- If a follow-up is clearly actionable for tomorrow, note it against tomorrow's
  calendar (don't create events unless asked).
- If they've got nothing, move on — don't push.

### 3. Wind down to sleep

- Remind them of **tomorrow's first commitment** (pull from Calendar
  `list_events` if not already known this session) so they can back-time sleep.
- If they shared Oura readiness earlier and it was low, gently suggest an earlier
  wind-down / target bedtime.
- Optionally offer to **stop the Spotify playlist** mention or switch to
  something quieter if they're heading to bed (the Spotify tools can't pause
  playback, so just suggest it in the app).

## Output Format

One short message: 💧 Recovery · 📝 Capture (the ask) · 😴 Wind-down.
Lead with hydration, end with a concrete target bedtime or first-thing reminder.

## Notes

- Brevity matters more here than in `/sauna` — they're winding down for sleep.
- Never fabricate calendar events or notes; confirm before saving anything.
- Notes/vault destinations: prefer PyNotes or Notion; the Obsidian `mogs` vault
  is a separate repo not available in-session.
- Pairs with `/sauna` (the in-sauna ritual).
