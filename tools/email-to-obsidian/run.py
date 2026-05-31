#!/usr/bin/env python3
"""Process the Gmail `mogs` queue into Obsidian notes.

Reads every email under the `mogs` label, classifies each with Claude, writes a
markdown note into the vault, marks the email as filed, and (optionally) commits
+ pushes the vault.

Usage:
    python run.py            # process the queue
    python run.py --dry-run  # classify + print, but don't write or touch Gmail

Configure via environment variables (see README.md):
    ANTHROPIC_API_KEY, MOGS_VAULT, MOGS_CREDENTIALS_FILE, ...
"""

from __future__ import annotations

import sys

import anthropic

from classifier import classify
from gmail_source import GmailSource
from vault_writer import commit_and_push, render, write_note
from youtube import enrich


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    source = GmailSource()

    emails = source.fetch_unfiled()
    if not emails:
        print("mogs queue is empty -- nothing to file.")
        return 0

    print(f"Found {len(emails)} email(s) in the mogs queue.\n")
    written = []
    for email in emails:
        # Pull in YouTube title/transcript so a "watch this" link becomes a real
        # note instead of a bare URL, and keep the note's Source clean. No-op for
        # emails without a YouTube link (beyond capping a long body).
        enriched = enrich(email.body)
        c = classify(client, email.subject, email.sender, enriched.classify_text)
        print(f"[{c.type}] {c.title}")
        print(f"    tags: {', '.join(c.tags)}")
        if c.action_items:
            print(f"    actions: {len(c.action_items)}")

        if dry_run:
            print("    --- dry run, note not written ---")
            print(render(c, email.sender, enriched.source_text))
            print()
            continue

        path = write_note(c, email.sender, enriched.source_text)
        written.append(path)
        print(f"    wrote {path}")
        source.mark_filed(email)
        print("    marked filed in Gmail\n")

    if not dry_run:
        commit_and_push(written)
        print(f"Done. Filed {len(written)} note(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
