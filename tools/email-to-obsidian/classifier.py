"""Classify an email into an Obsidian note type using the Anthropic SDK.

Uses structured outputs (a Pydantic schema via ``messages.parse``) so the result
is always valid and typed, plus prompt caching on the stable system prompt so
repeated runs only pay full price for the first message.
"""

from __future__ import annotations

import os
from typing import List

import anthropic
from pydantic import BaseModel, Field

from taxonomy import ALLOWED_TYPES, DEFAULT_TYPE, taxonomy_for_prompt

# Default to the most capable model. Override with MODEL=claude-haiku-4-5 (or
# claude-sonnet-4-6) for cheaper high-volume runs -- classification is simple
# enough that a smaller model is usually fine.
MODEL = os.environ.get("MOGS_MODEL", "claude-opus-4-8")

# Cap how much of the body we send -- keeps token cost predictable on long
# newsletters. The forwarder's note and the opening of the email carry the signal.
MAX_BODY_CHARS = int(os.environ.get("MOGS_MAX_BODY_CHARS", "6000"))


class Classification(BaseModel):
    """Structured result the model must return for each email."""

    type: str = Field(description=f"One of: {', '.join(ALLOWED_TYPES)}")
    title: str = Field(description="A short, specific note title (no date prefix).")
    tags: List[str] = Field(
        default_factory=list,
        description="Lowercase hashtag-style tags WITHOUT the '#', e.g. ['pr', 'marketing'].",
    )
    summary: str = Field(description="A one or two line gist of the note.")
    action_items: List[str] = Field(
        default_factory=list,
        description="Concrete next steps. Empty list if there is nothing to do.",
    )


def _system_prompt() -> str:
    return (
        "You file forwarded emails into an Obsidian vault. For each email decide "
        "which single note type it belongs to, then produce a clean title, tags, "
        "a short summary, and any action items.\n\n"
        "Note types:\n"
        f"{taxonomy_for_prompt()}\n\n"
        "Rules:\n"
        "- When an email is a forward WITH an added note from the sender, that "
        "note is the primary intent. Classify on the note, not the quoted email.\n"
        "- Prefer 'task' over 'reading' whenever the forwarder expresses an "
        "intent to act ('let's...', 'we should...', 'figure out...').\n"
        "- Tags are lowercase, no '#', no spaces (use hyphens). Always include a "
        "tag for the broad topic.\n"
        "- Keep the title specific and human; do not just echo the email subject."
    )


def classify(
    client: anthropic.Anthropic,
    subject: str,
    sender: str,
    body: str,
) -> Classification:
    body = (body or "").strip()
    if len(body) > MAX_BODY_CHARS:
        body = body[:MAX_BODY_CHARS] + "\n...[truncated]"

    user_content = (
        f"From: {sender}\n"
        f"Subject: {subject}\n\n"
        f"Body:\n{body}"
    )

    response = client.messages.parse(
        model=MODEL,
        max_tokens=1024,
        # System prompt is stable across every email -> cache it. The structured
        # output schema is also cached server-side for 24h automatically.
        system=[
            {
                "type": "text",
                "text": _system_prompt(),
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_content}],
        output_format=Classification,
    )

    result = response.parsed_output
    if result is None:
        # Refusal or unparseable -- fall back to a safe reference note.
        result = Classification(
            type=DEFAULT_TYPE,
            title=subject or "Untitled",
            tags=["mogs"],
            summary="(could not classify automatically)",
            action_items=[],
        )

    if result.type not in ALLOWED_TYPES:
        result.type = DEFAULT_TYPE

    # Make sure every note carries the flow tag.
    if "mogs" not in result.tags:
        result.tags.insert(0, "mogs")

    return result
