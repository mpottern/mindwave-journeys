"""Render a Classification into a markdown note and write it into the vault.

The vault is assumed to be a git repository. Notes land in
``<VAULT>/<FLOW_DIR>/<TypeSubfolder>/<date>-<slug>.md``. Optionally commits (and
pushes) so the change syncs to your other devices.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import subprocess
from pathlib import Path

from classifier import Classification
from taxonomy import subfolder_for

VAULT = Path(os.environ.get("MOGS_VAULT", "")).expanduser()
FLOW_DIR = os.environ.get("MOGS_FLOW_DIR", "Flow")
GIT_COMMIT = os.environ.get("MOGS_GIT_COMMIT", "1") == "1"
GIT_PUSH = os.environ.get("MOGS_GIT_PUSH", "0") == "1"


def _slug(text: str, max_len: int = 60) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return (text or "note")[:max_len].strip("-")


def _frontmatter(c: Classification, sender: str, created: str) -> str:
    tags = ", ".join(c.tags)
    lines = [
        "---",
        f"type: {c.type}",
        f"created: {created}",
        "source: email",
        f"from: {sender}",
        f"tags: [{tags}]",
    ]
    if c.type == "task":
        lines.append("status: todo")
    lines.append("---")
    return "\n".join(lines)


def render(c: Classification, sender: str, body: str) -> str:
    created = dt.date.today().isoformat()
    parts = [_frontmatter(c, sender, created), "", f"# {c.title}", ""]
    if c.summary:
        parts += [f"> {c.summary}", ""]
    if c.action_items:
        parts.append("## Action items")
        parts += [f"- [ ] {item}" for item in c.action_items]
        parts.append("")
    parts += ["## Source", "", body.strip(), ""]
    return "\n".join(parts)


def write_note(c: Classification, sender: str, body: str) -> Path:
    if not VAULT or not VAULT.exists():
        raise SystemExit(
            f"Vault path {str(VAULT)!r} does not exist. Set MOGS_VAULT to your "
            "Obsidian vault (a git repo)."
        )
    folder = VAULT / FLOW_DIR / subfolder_for(c.type)
    folder.mkdir(parents=True, exist_ok=True)

    created = dt.date.today().isoformat()
    base = f"{created}-{_slug(c.title)}"
    path = folder / f"{base}.md"
    n = 2
    while path.exists():
        path = folder / f"{base}-{n}.md"
        n += 1

    path.write_text(render(c, sender, body), encoding="utf-8")
    return path


def commit_and_push(paths: list[Path]) -> None:
    if not GIT_COMMIT or not paths:
        return
    rels = [str(p.relative_to(VAULT)) for p in paths]
    subprocess.run(["git", "-C", str(VAULT), "add", *rels], check=True)
    msg = f"mogs: file {len(paths)} note(s) from email"
    # Don't fail the whole run if there's nothing staged (e.g. dupes).
    subprocess.run(["git", "-C", str(VAULT), "commit", "-m", msg], check=False)
    if GIT_PUSH:
        subprocess.run(["git", "-C", str(VAULT), "push"], check=False)
