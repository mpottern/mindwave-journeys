# Oura readout (`oura`)

A tiny, dependency-free fetcher for the four numbers the `/sauna` ritual asks
for — **Readiness, Sleep score, HRV, and resting heart rate** — so the skill can
pull them live instead of having you read them off the app.

```
OURA_TOKEN ──► Oura API v2 ──► Readiness / Sleep / HRV / Resting HR
              (daily_readiness, daily_sleep, sleep)
```

## Files

| File | Purpose |
|---|---|
| `run.py` | Entry point — prints the readout (human or `--json`). |
| `oura.py` | Stdlib-only Oura API v2 client. |

No third-party packages — it uses Python's standard library, so there's no
`requirements.txt` and no venv needed.

## One-time setup

1. Create a **personal access token** at
   <https://cloud.ouraring.com/personal-access-tokens>.
2. Drop it in `.env`:
   ```bash
   cd tools/oura
   cp .env.example .env   # then paste your token into OURA_TOKEN
   ```

## Run it

```bash
set -a; source .env; set +a

python run.py          # human-readable digest
python run.py --json   # JSON, e.g. {"day": "...", "readiness": 82, ...}
```

The `/sauna` skill runs `python run.py --json` and interprets the numbers
against tomorrow's calendar. If `OURA_TOKEN` is missing or the ring hasn't
synced, the command exits non-zero and the skill falls back to asking you for
the numbers by hand.

## Notes

- **Resting HR** is reported as the night's `lowest_heart_rate`; **HRV** is the
  overnight average rMSSD (`average_hrv`) — the same figures the Oura app shows.
- **Secrets:** `.env` is git-ignored — never commit your token.
- Looks back a few days and uses the most recent day with data, so an unsynced
  morning still returns last night's numbers.
