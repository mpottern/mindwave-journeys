# Email → Obsidian flow (`mogs`)

Forward an email to **`michael+mogs@denverzenden.com`**, and this tool reads it from
the Gmail `mogs` label, asks Claude *"what kind of note is this?"*, and files a
markdown note into your Obsidian vault — routed by type, with frontmatter, tags,
a summary, and any action items.

```
forward email ──► Gmail `mogs` label ──► Claude classifies ──► Flow/<Type>/note.md
                                          (task/idea/reference/        (committed to
                                           journal/meeting/reading)     your vault repo)
```

## Files

| File | Purpose |
|---|---|
| `run.py` | Entry point — processes the whole `mogs` queue. |
| `taxonomy.py` | The note types + folder mapping. **Edit this to change your buckets.** |
| `classifier.py` | Calls Claude with structured output + prompt caching. |
| `gmail_source.py` | Reads the `mogs` label, marks mail filed. |
| `vault_writer.py` | Renders markdown, writes to the vault, commits/pushes. |

## One-time setup

1. **Python deps**
   ```bash
   cd tools/email-to-obsidian
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Gmail filter + label** (in Gmail settings, once):
   - Filter `To: michael+mogs@denverzenden.com` → apply label **`mogs`** (and optionally Skip the Inbox).
   - The label already exists in your account.
   - The hub is whichever account authorizes `token.json` (step 3); forward mail
     so it lands there with the `mogs` label. Override the address with
     `MOGS_FORWARD_ADDR` if you use a different mailbox.

3. **Gmail API credentials**
   - In [Google Cloud Console](https://console.cloud.google.com/): create a project → enable the **Gmail API** → **OAuth client ID** of type **Desktop app** → download the JSON as `credentials.json` into this folder.
   - Add your own address as a test user on the OAuth consent screen.

4. **Config**
   ```bash
   cp .env.example .env   # then edit: ANTHROPIC_API_KEY, MOGS_VAULT, ...
   set -a; source .env; set +a
   ```
   `MOGS_VAULT` must point at your Obsidian vault, which should be a **git repo**.

## Run it

```bash
# See what it would do — classifies and prints the notes, touches nothing:
python run.py --dry-run

# For real — writes notes, marks mail filed, commits the vault:
python run.py
```

First run opens a browser to authorize Gmail; the token is cached in `token.json`
for non-interactive runs afterward.

## Hands-off (cron)

Once `token.json` exists, schedule it (set `MOGS_GIT_PUSH=1` so notes sync):

```cron
*/10 * * * * cd /path/to/tools/email-to-obsidian && . .venv/bin/activate && set -a && . .env && set +a && python run.py >> mogs.log 2>&1
```

## Notes

- **The vault is a separate git repo from `mindwave-journeys`.** `MOGS_VAULT`
  must point at your **Obsidian vault**, not at this repo. This tool lives in
  `mindwave-journeys`, but it writes and commits notes into whatever vault repo
  `MOGS_VAULT` points to. Don't set `MOGS_VAULT` to the `mindwave-journeys`
  checkout.
- **Model:** defaults to `claude-opus-4-8`. For cheaper high-volume runs set
  `MOGS_MODEL=claude-haiku-4-5`.
- **Cost control:** the stable system prompt is prompt-cached and the email body
  is capped at `MOGS_MAX_BODY_CHARS` (default 6000).
- **Reprocessing:** filed mail loses the `mogs` label and gains `mogs-filed`, so
  re-running never double-files.
- **Secrets:** `.env`, `credentials.json`, and `token.json` are git-ignored —
  never commit them.
