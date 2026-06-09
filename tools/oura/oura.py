"""Minimal Oura API v2 client (stdlib only).

Pulls the metrics the `/sauna` ritual cares about — Readiness, Sleep score,
HRV, and resting heart rate — using a personal access token.

Get a token at https://cloud.ouraring.com/personal-access-tokens and put it in
the environment as OURA_TOKEN (see .env.example). No third-party packages.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta

API_ROOT = "https://api.ouraring.com/v2/usercollection"


class OuraError(RuntimeError):
    """Raised when the Oura API can't be reached or returns an error."""


@dataclass
class Readout:
    """The numbers the sauna skill reads off — any field may be None."""

    day: str | None = None
    readiness: int | None = None          # daily readiness score, 0-100
    sleep_score: int | None = None        # daily sleep score, 0-100
    hrv: int | None = None                # average overnight HRV, ms (rMSSD)
    resting_hr: int | None = None         # lowest overnight heart rate, bpm
    average_hr: int | None = None         # average overnight heart rate, bpm

    def is_empty(self) -> bool:
        return all(
            v is None
            for v in (self.readiness, self.sleep_score, self.hrv, self.resting_hr)
        )


def _get(path: str, token: str, params: dict) -> list[dict]:
    url = f"{API_ROOT}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:200]
        if exc.code in (401, 403):
            raise OuraError(
                "Oura rejected the token (401/403). Check OURA_TOKEN is a valid "
                "personal access token."
            ) from exc
        raise OuraError(f"Oura API error {exc.code} on {path}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise OuraError(f"Could not reach the Oura API: {exc.reason}") from exc
    return payload.get("data", [])


def _latest(rows: list[dict]) -> dict | None:
    """Most recent document by its `day` field."""
    dated = [r for r in rows if r.get("day")]
    return max(dated, key=lambda r: r["day"]) if dated else None


def fetch(token: str, lookback_days: int = 3) -> Readout:
    """Fetch the latest available readout, looking back a few days for freshness."""
    if not token:
        raise OuraError("OURA_TOKEN is not set.")

    end = date.today()
    start = end - timedelta(days=lookback_days)
    window = {"start_date": start.isoformat(), "end_date": end.isoformat()}

    readiness = _latest(_get("daily_readiness", token, window))
    sleep_score = _latest(_get("daily_sleep", token, window))
    # The detailed `sleep` endpoint carries the physiological numbers.
    sleep_doc = _latest(_get("sleep", token, window))

    out = Readout()
    days = []
    if readiness:
        out.readiness = readiness.get("score")
        days.append(readiness.get("day"))
    if sleep_score:
        out.sleep_score = sleep_score.get("score")
        days.append(sleep_score.get("day"))
    if sleep_doc:
        out.hrv = sleep_doc.get("average_hrv")
        out.resting_hr = sleep_doc.get("lowest_heart_rate")
        out.average_hr = sleep_doc.get("average_heart_rate")
        days.append(sleep_doc.get("day"))

    out.day = max((d for d in days if d), default=None)
    return out
