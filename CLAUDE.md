# mindwave-journeys

Personal site + automation flows. The `tools/` directory holds standalone
workflows (see each tool's README); `mindwave-journeys-site/` is the static site.

## Skills

Reusable rituals in `.claude/skills/`:

- **`/sauna`** — In-sauna wind-down. Triggers on "Sauna, I just got in" / "sauna
  session". Runs: relaxing Spotify playlist → read the `mogs` reading queue →
  today recap + tomorrow's calendar with insights → Oura check-in (pulls
  Readiness / Sleep / HRV / resting HR live via `tools/oura/`, falling back to
  asking the user, then interprets for tomorrow's load).

- **`/post-sauna`** — Cool-down bookend. Triggers on "post sauna" / "just got
  out". Runs: hydration/recovery nudge → capture any ideas/tasks/journal thoughts
  that surfaced (saves via PyNotes or Notion, routed like the `mogs` buckets) →
  wind-down to sleep with tomorrow's first commitment + a target bedtime.

- **`/skill-builder`** — Guide for creating/auditing skills.

## Notes flow (`mogs`)

`tools/email-to-obsidian/` classifies forwarded email into an Obsidian vault.
That vault is a **separate git repo** (`MOGS_VAULT`) — not this checkout. The
`/sauna` queue reads unfiled items straight from the Gmail `mogs` label instead.

## Oura (`tools/oura/`)

Dependency-free Oura API v2 fetcher used by `/sauna`. `python tools/oura/run.py
--json` prints Readiness / Sleep / HRV / resting HR; needs `OURA_TOKEN` (a
personal access token) in `tools/oura/.env`. No token → the skill falls back to
asking for the numbers by hand.
