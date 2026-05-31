#!/usr/bin/env bash
# Convenience runner for the email -> Obsidian flow.
#
# Activates the local venv, loads .env, and runs the pipeline from anywhere --
# so a fresh terminal doesn't need the activate/source dance.
#
#   ./mogs.sh            # process the mogs queue for real
#   ./mogs.sh --dry-run  # classify + print, write nothing
#
# Run it as a file (./mogs.sh), not by pasting its contents into the shell.
set -euo pipefail

# cd to this script's directory so relative paths (.venv, .env) resolve no
# matter where it's invoked from.
cd "$(dirname "${BASH_SOURCE[0]}")"

# shellcheck disable=SC1091
source .venv/bin/activate

# Export everything defined in .env into the environment for run.py.
set -a
# shellcheck disable=SC1091
source .env
set +a

exec python run.py "$@"
