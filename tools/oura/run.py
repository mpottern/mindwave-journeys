#!/usr/bin/env python3
"""Print today's Oura readout for the `/sauna` ritual.

Reads OURA_TOKEN from the environment and prints Readiness, Sleep score, HRV,
and resting heart rate — either as a human digest or as JSON for the skill to
parse.

Usage:
    python run.py            # human-readable digest
    python run.py --json     # machine-readable JSON (for the /sauna skill)
    python run.py --date 2026-06-09   # (reserved) pin a specific day window

Configure via environment variables (see .env.example):
    OURA_TOKEN   personal access token from cloud.ouraring.com
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict

from oura import OuraError, Readout, fetch


def _digest(r: Readout) -> str:
    day = f" ({r.day})" if r.day else ""
    if r.is_empty():
        return (
            "No Oura data found for the last few days" + day + ". Wear the ring "
            "overnight and sync the app, then try again."
        )

    def line(label: str, value, unit: str = "") -> str:
        shown = f"{value}{unit}" if value is not None else "—"
        return f"  {label:<12} {shown}"

    return "\n".join(
        [
            f"Oura readout{day}:",
            line("Readiness", r.readiness),
            line("Sleep", r.sleep_score),
            line("HRV", r.hrv, " ms"),
            line("Resting HR", r.resting_hr, " bpm"),
            line("Avg HR", r.average_hr, " bpm"),
        ]
    )


def main() -> int:
    as_json = "--json" in sys.argv
    token = os.environ.get("OURA_TOKEN", "")

    try:
        readout = fetch(token)
    except OuraError as exc:
        if as_json:
            print(json.dumps({"error": str(exc)}))
        else:
            print(f"Oura: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(asdict(readout)) if as_json else _digest(readout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
