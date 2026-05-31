"""Enrich emails that are essentially just a YouTube link.

A forwarded "watch this" email often has nothing but a URL in the body, which
makes for a thin, useless note. When we spot a YouTube link we pull the video's
title and channel (via the public oEmbed endpoint -- no API key) and, when
available, the transcript (via the optional ``youtube-transcript-api`` package).
The enriched text feeds both the classifier (so a bare link is filed sensibly,
with real action items) and the rendered note's Source section.

Everything here is best-effort: network errors, a missing transcript, or the
optional dependency not being installed all degrade gracefully to whatever we
could get. A bare link is better than a crashed run, so nothing here raises into
the pipeline.
"""

from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import List, Optional, Tuple

# youtu.be/<id>, youtube.com/watch?v=<id>, /embed/<id>, /shorts/<id>, /live/<id>
_PATTERNS = [
    re.compile(r"youtu\.be/([A-Za-z0-9_-]{11})"),
    re.compile(r"youtube\.com/watch\?(?:[^\s]*&)?v=([A-Za-z0-9_-]{11})"),
    re.compile(r"youtube\.com/(?:embed|shorts|v|live)/([A-Za-z0-9_-]{11})"),
]

OEMBED = "https://www.youtube.com/oembed"
TIMEOUT = float(os.environ.get("MOGS_HTTP_TIMEOUT", "10"))
# Cap transcript length so a long video doesn't blow up token cost or note size.
MAX_TRANSCRIPT_CHARS = int(os.environ.get("MOGS_MAX_TRANSCRIPT_CHARS", "8000"))
# Cap a non-video note's Source section so a long newsletter doesn't produce a
# giant, tracking-link-laden note. Video notes are exempt -- their Source is the
# clean transcript block, already bounded by MAX_TRANSCRIPT_CHARS.
MAX_SOURCE_CHARS = int(os.environ.get("MOGS_MAX_SOURCE_CHARS", "2000"))


@dataclass
class Video:
    video_id: str
    url: str
    title: Optional[str] = None
    author: Optional[str] = None
    transcript: Optional[str] = None


@dataclass
class Enrichment:
    """Two views of an email body for the pipeline."""

    classify_text: str  # full signal for the model: original body + video blocks
    source_text: str  # clean text for the note's Source section
    has_video: bool


def extract_video_ids(text: str) -> List[str]:
    """Return unique YouTube video IDs found in text, in order of appearance."""
    seen: dict[str, None] = {}
    for pat in _PATTERNS:
        for m in pat.finditer(text or ""):
            seen.setdefault(m.group(1), None)
    return list(seen)


def _fetch_metadata(video_id: str) -> Tuple[Optional[str], Optional[str]]:
    """Title + channel via the public oEmbed endpoint. (None, None) on failure."""
    watch = f"https://www.youtube.com/watch?v={video_id}"
    q = urllib.parse.urlencode({"url": watch, "format": "json"})
    try:
        with urllib.request.urlopen(f"{OEMBED}?{q}", timeout=TIMEOUT) as r:
            data = json.load(r)
        return data.get("title"), data.get("author_name")
    except Exception:
        return None, None


def _fetch_transcript(video_id: str) -> Optional[str]:
    """Plain-text transcript via youtube-transcript-api, capped. None if absent."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return None
    try:
        segments = YouTubeTranscriptApi().fetch(video_id)
        # Support both the newer object API and the older list-of-dicts API.
        parts = [getattr(s, "text", None) or s.get("text", "") for s in segments]
    except Exception:
        try:
            segments = YouTubeTranscriptApi.get_transcript(video_id)
            parts = [s.get("text", "") for s in segments]
        except Exception:
            return None
    text = " ".join(p for p in parts if p).strip()
    if not text:
        return None
    if len(text) > MAX_TRANSCRIPT_CHARS:
        text = text[:MAX_TRANSCRIPT_CHARS].rstrip() + " ...[transcript truncated]"
    return text


def describe(video_id: str) -> Video:
    """Best-effort metadata + transcript for a single video id."""
    title, author = _fetch_metadata(video_id)
    return Video(
        video_id=video_id,
        url=f"https://youtu.be/{video_id}",
        title=title,
        author=author,
        transcript=_fetch_transcript(video_id),
    )


def _video_block(v: Video) -> str:
    lines = [f"## Video: {v.title or v.url}"]
    if v.author:
        lines.append(f"- Channel: {v.author}")
    lines.append(f"- Link: {v.url}")
    if v.transcript:
        lines += ["", "### Transcript", "", v.transcript]
    else:
        lines += ["", "_(no transcript available)_"]
    return "\n".join(lines)


def enrich(body: str) -> Enrichment:
    """Resolve a raw email body into model-facing and note-facing text.

    For a forwarded YouTube link the note's Source becomes a clean
    title/channel/transcript block -- the forwarded email's signature and
    tracking-link cruft are dropped -- while the classifier still sees the
    original text *and* the transcript for maximum signal. For everything else
    the Source is the body, capped so a long newsletter doesn't produce a giant
    note. Safe to call on every email.
    """
    body = body or ""
    ids = extract_video_ids(body)

    if not ids:
        source = body.strip()
        if len(source) > MAX_SOURCE_CHARS:
            source = source[:MAX_SOURCE_CHARS].rstrip() + "\n\n...[truncated]"
        return Enrichment(classify_text=body, source_text=source, has_video=False)

    blocks = "\n\n".join(_video_block(describe(vid)) for vid in ids)
    original = body.strip()
    classify_text = f"{original}\n\n{blocks}".strip() if original else blocks
    return Enrichment(classify_text=classify_text, source_text=blocks, has_video=True)


if __name__ == "__main__":  # quick manual check: python youtube.py <url-or-id>
    import sys

    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    print(enrich(arg).source_text)
