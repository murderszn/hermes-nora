#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Bootstrapping Nora from $ROOT"

if [ -d "$ROOT/persona" ]; then
  echo "  ✓ Persona files found"
fi

if [ -d "$ROOT/skills" ]; then
  echo "  ✓ Skills found"
fi

if [ -d "$ROOT/tools" ]; then
  echo "  ✓ Tools found"
fi

echo ""
echo "Next: configure your Hermes agent to load the Nora addon from:"
echo "  $ROOT"