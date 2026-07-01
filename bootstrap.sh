#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Bootstrapping Nora from $ROOT"
echo ""

count_skills() {
  find "$ROOT/skills" -name 'SKILL.md' 2>/dev/null | wc -l | tr -d ' '
}

if [ -f "$ROOT/hermes/SOUL.md" ]; then
  lines=$(grep -cve '^\s*$' -e '^#' -e '^<!--' -e '^-->' -e '^\s*\*' "$ROOT/hermes/SOUL.md" 2>/dev/null || echo 0)
  if [ "$lines" -gt 5 ]; then
    echo "  ✓ Soul document (hermes/SOUL.md)"
  else
    echo "  ○ Soul template present — customize hermes/SOUL.md"
  fi
fi

if [ -d "$ROOT/persona" ]; then
  echo "  ✓ Persona / roles (persona/)"
fi

if [ -d "$ROOT/skills" ]; then
  n=$(count_skills)
  echo "  ✓ Skills library ($n skills)"
fi

if [ -d "$ROOT/tools" ]; then
  echo "  ✓ Tools (tools/)"
fi

if [ -d "$ROOT/dashboard" ]; then
  echo "  ✓ Dashboard (dashboard/)"
fi

echo ""
echo "Onboard (recommended — wizard for persona + channel + gateway):"
echo "  $ROOT/scripts/onboard.sh"
echo ""
echo "Activate only (Hermes already set up):"
echo "  $ROOT/scripts/activate.sh"
echo "  $ROOT/scripts/activate.sh --merge-only   # keep your LLM provider"
echo ""
echo "Health check:"
echo "  $ROOT/scripts/doctor.sh"
echo ""
echo "Docs:     $ROOT/persona/hermes-setup.md"
echo "Channels: $ROOT/persona/channels.md"
echo "Skills:   $ROOT/skills/README.md"