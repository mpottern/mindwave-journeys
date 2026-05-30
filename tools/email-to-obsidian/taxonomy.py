"""Note taxonomy for the email -> Obsidian flow.

Edit this file to add, remove, or rename note types. The `NOTE_TYPES` keys are
the values Claude is allowed to return; each maps to (vault subfolder, human
description used to steer the classifier).

Keep the descriptions concrete -- they are the only thing the model uses to
decide which bucket an email belongs in.
"""

from __future__ import annotations

# type key -> (Flow/ subfolder, description shown to the classifier)
NOTE_TYPES: dict[str, tuple[str, str]] = {
    "task": (
        "Tasks",
        "Something to do or follow up on. Forwarded emails with an added note "
        'like "let\'s figure out how to..." or "we should..." are tasks -- the '
        "forwarder's note is the real intent, the quoted email is just source "
        "material.",
    ),
    "idea": (
        "Ideas",
        "A thought, concept, product/marketing idea, or thing worth exploring "
        "later. Not yet an actionable task.",
    ),
    "reference": (
        "References",
        "Information to keep for later lookup: a fact, link, contact, receipt, "
        "confirmation, or document. No action required.",
    ),
    "journal": (
        "Journal",
        "A personal reflection, status update, or log entry about what happened.",
    ),
    "meeting": (
        "Meetings",
        "A meeting invite, agenda, recap, or notes tied to a specific meeting "
        "or event with people and a time.",
    ),
    "reading": (
        "Reading",
        "An article, newsletter, or long-form piece forwarded purely to read "
        "later, with no added action or intent from the forwarder.",
    ),
}

# Fallback bucket if the model returns something unexpected.
DEFAULT_TYPE = "reference"

ALLOWED_TYPES = list(NOTE_TYPES.keys())


def subfolder_for(note_type: str) -> str:
    return NOTE_TYPES.get(note_type, NOTE_TYPES[DEFAULT_TYPE])[0]


def taxonomy_for_prompt() -> str:
    lines = []
    for key, (_folder, desc) in NOTE_TYPES.items():
        lines.append(f"- {key}: {desc}")
    return "\n".join(lines)
