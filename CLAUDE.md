# mindwave-journeys

Personal site + automation flows. The `tools/` directory holds standalone
workflows (see each tool's README); `mindwave-journeys-site/` is the static site.

## Skills

Reusable rituals in `.claude/skills/`:

- **`/sauna`** — In-sauna wind-down. Triggers on "Sauna, I just got in" / "sauna
  session". Runs: relaxing Spotify playlist → read the `mogs` reading queue →
  today recap + tomorrow's calendar with insights → Oura check-in (asks the user
  for Readiness / Sleep / HRV / resting HR and interprets for tomorrow's load).

- **`/post-sauna`** — Cool-down bookend. Triggers on "post sauna" / "just got
  out". Runs: hydration/recovery nudge → capture any ideas/tasks/journal thoughts
  that surfaced (saves via PyNotes or Notion, routed like the `mogs` buckets) →
  wind-down to sleep with tomorrow's first commitment + a target bedtime.

- **`/skill-builder`** — Guide for creating/auditing skills.

## Notes flow (`mogs`)

`tools/email-to-obsidian/` classifies forwarded email into an Obsidian vault.
That vault is a **separate git repo** (`MOGS_VAULT`) — not this checkout. The
`/sauna` queue reads unfiled items straight from the Gmail `mogs` label instead.
