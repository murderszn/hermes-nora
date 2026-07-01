#!/usr/bin/env bash
# Nora health check — wiring, secrets, gateway.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

PYTHON="${HERMES_PYTHON:-}"
if [ -z "$PYTHON" ] && [ -x "$HERMES_HOME/hermes-agent/venv/bin/python" ]; then
  PYTHON="$HERMES_HOME/hermes-agent/venv/bin/python"
fi
PYTHON="${PYTHON:-python3}"

exec "$PYTHON" "$ROOT/tools/doctor.py" --nora-root "$ROOT" --hermes-home "$HERMES_HOME" "$@"