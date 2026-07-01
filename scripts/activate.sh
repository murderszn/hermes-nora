#!/usr/bin/env bash
# Install Nora's soul + skills into the live Hermes home (~/.hermes).
# This is what makes Discord (and every channel) talk as Nora.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

echo "  ◉  Activate Nora → Hermes"
echo "     Nora root:   $ROOT"
echo "     Hermes home: $HERMES_HOME"
echo ""

if [ ! -f "$HERMES_HOME/config.yaml" ]; then
  echo "Error: Hermes not set up. Run: hermes setup"
  exit 1
fi

PYTHON="${HERMES_PYTHON:-}"
if [ -z "$PYTHON" ] && [ -x "$HOME/.hermes/hermes-agent/venv/bin/python" ]; then
  PYTHON="$HOME/.hermes/hermes-agent/venv/bin/python"
fi
PYTHON="${PYTHON:-python3}"

ACTIVATE_ARGS=(--nora-root "$ROOT" --hermes-home "$HERMES_HOME")
if [[ "${1:-}" == "--merge-only" ]]; then
  ACTIVATE_ARGS+=(--merge-only)
fi

"$PYTHON" "$ROOT/tools/activate_nora.py" "${ACTIVATE_ARGS[@]}"

if [ -f "$ROOT/.env" ]; then
  "$PYTHON" "$ROOT/tools/sync_env.py" --nora-root "$ROOT" --hermes-home "$HERMES_HOME"
else
  echo "  ○ No $ROOT/.env — Discord secrets stay in $HERMES_HOME/.env"
fi

echo ""
echo "  Nora is live in Hermes."
echo "  Start Discord: hermes gateway run"