"""Detect a YouTube link in an email and fetch its title + transcript.

Title/channel come from YouTube's public oEmbed endpoint (no API key). The
transcript comes from `youtube-transcript-api` (the video's captions/auto-captions).
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional

# Matches watch?v=, youtu.be/, /shorts/, /embed/, /live/ and grabs the 11-char id.
_YT_RE = re.compile(
    r"(?:https?://)?(?:www\.|m\.)?"
    r"(?:youtube\.com/(?:watch\?(?:[^ \n]*&)?v=|shorts/|embed/|live/)|youtu\.be/)"
    r"([A-Za-z0-9_-]{11})",
    re.IGNORECASE,
)


@dataclass
class Video:
    video_id: str
    url: str
    title: str
    channel: str
    transcript: str  # empty string if none available


def find_video_id(text: str) -> Optional[str]:
    m = _YT_RE.search(text or "")
    return m.group(1) if m else None


def _fetch_meta(video_id: str) -> tuple[str, str]:
    """Return (title, channel) via oEmbed; fall back to the id on failure."""
    watch = f"https://www.youtube.com/watch?v={video_id}"
    oembed = "https://www.youtube.com/oembed?" + urllib.parse.urlencode(
        {"url": watch, "format": "json"}
    )
    try:
        req = urllib.request.Request(oembed, headers={"User-Agent": "mogs/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
        return data.get("title") or video_id, data.get("author_name") or ""
    except Exception:
        return video_id, ""


def _fetch_transcript(video_id: str) -> str:
    """Best-effort transcript. Empty string if captions are unavailable.

    Handles both the 1.x instance API (`.fetch`) and the older 0.6.x
    classmethod (`.get_transcript`).
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return ""

    # 1.x: instance .fetch() -> iterable of snippet objects with .text
    try:
        fetched = YouTubeTranscriptApi().fetch(video_id)
        return " ".join(getattr(s, "text", "") for s in fetched).strip()
    except AttributeError:
        pass
    except Exception:
        return ""

    # 0.6.x: classmethod returning list[dict]
    try:
        data = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(d.get("text", "") for d in data).strip()
    except Exception:
        return ""


def fetch(video_id: str) -> Video:
    title, channel = _fetch_meta(video_id)
    transcript = _fetch_transcript(video_id)
    return Video(
        video_id=video_id,
        url=f"https://www.youtube.com/watch?v={video_id}",
        title=title,
        channel=channel,
        transcript=transcript,
    )
