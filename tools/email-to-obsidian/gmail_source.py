"""Read forwarded emails from the Gmail `mogs` label.

Uses OAuth desktop credentials. On first run it opens a browser to authorize,
then caches the token in MOGS_TOKEN_FILE so later runs are non-interactive
(suitable for cron).
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# gmail.modify lets us read messages AND move the label off processed mail so we
# don't re-file the same email twice.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

CREDENTIALS_FILE = os.environ.get("MOGS_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE = os.environ.get("MOGS_TOKEN_FILE", "token.json")
LABEL_NAME = os.environ.get("MOGS_LABEL", "mogs")
# Label applied after a message is filed, so it isn't picked up again.
DONE_LABEL_NAME = os.environ.get("MOGS_DONE_LABEL", "mogs-filed")


@dataclass
class Email:
    id: str
    thread_id: str
    sender: str
    subject: str
    body: str


def _service():
    creds: Optional[Credentials] = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def _decode(data: str) -> str:
    return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", "replace")


def _extract_body(payload: dict) -> str:
    """Walk the MIME tree and return the best plain-text body."""
    # Prefer text/plain; fall back to the first text/* part.
    plain, fallback = None, None

    def walk(part):
        nonlocal plain, fallback
        mime = part.get("mimeType", "")
        body = part.get("body", {})
        data = body.get("data")
        if data:
            if mime == "text/plain" and plain is None:
                plain = _decode(data)
            elif mime.startswith("text/") and fallback is None:
                fallback = _decode(data)
        for sub in part.get("parts", []) or []:
            walk(sub)

    walk(payload)
    return plain or fallback or ""


def _header(headers: List[dict], name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def _label_id(svc, name: str, create: bool = False) -> Optional[str]:
    labels = svc.users().labels().list(userId="me").execute().get("labels", [])
    for lbl in labels:
        if lbl["name"] == name:
            return lbl["id"]
    if create:
        created = (
            svc.users()
            .labels()
            .create(userId="me", body={"name": name})
            .execute()
        )
        return created["id"]
    return None


class GmailSource:
    def __init__(self):
        self.svc = _service()
        self.label_id = _label_id(self.svc, LABEL_NAME)
        if not self.label_id:
            raise SystemExit(
                f"Label {LABEL_NAME!r} not found in Gmail. Create it and add a "
                f"filter for To: mpottern+{LABEL_NAME}@gmail.com first."
            )
        self.done_label_id = _label_id(self.svc, DONE_LABEL_NAME, create=True)

    def fetch_unfiled(self, limit: int = 25) -> List[Email]:
        resp = (
            self.svc.users()
            .messages()
            .list(userId="me", labelIds=[self.label_id], maxResults=limit)
            .execute()
        )
        out: List[Email] = []
        for ref in resp.get("messages", []):
            msg = (
                self.svc.users()
                .messages()
                .get(userId="me", id=ref["id"], format="full")
                .execute()
            )
            payload = msg.get("payload", {})
            headers = payload.get("headers", [])
            out.append(
                Email(
                    id=msg["id"],
                    thread_id=msg.get("threadId", ""),
                    sender=_header(headers, "From"),
                    subject=_header(headers, "Subject"),
                    body=_extract_body(payload),
                )
            )
        return out

    def mark_filed(self, email: Email) -> None:
        """Remove the `mogs` label and add `mogs-filed` so it isn't reprocessed."""
        self.svc.users().messages().modify(
            userId="me",
            id=email.id,
            body={
                "removeLabelIds": [self.label_id],
                "addLabelIds": [self.done_label_id] if self.done_label_id else [],
            },
        ).execute()
