#!/usr/bin/env bash
# Sync the nora dev workspace → hermes-nora git repo.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${HERMES_NORA_REPO:-$HOME/hermes-nora}"

if [ ! -d "$DEST/.git" ]; then
  echo "Error: hermes-nora repo not found at $DEST"
  echo "Set HERMES_NORA_REPO or clone: gh repo clone murderszn/hermes-nora"
  exit 1
fi

WEB="$DEST/website"
mkdir -p "$WEB" "$DEST/skills" "$DEST/persona" "$DEST/tools" "$DEST/scripts" "$DEST/hermes"

echo "Syncing Nora workspace → $DEST"
echo ""

# Website (nora keeps site at repo root; hermes-nora uses website/)
for f in index.html docs.html roadmap.html styles.css docs.css roadmap.css \
         main.js docs.js site-links.js shader-banner.js icons.svg LICENSE; do
  if [ -f "$SRC/$f" ]; then
    cp "$SRC/$f" "$WEB/"
    echo "  website/$f"
  fi
done

if [ -d "$SRC/public" ]; then
  rsync -a --delete "$SRC/public/" "$WEB/public/"
  echo "  website/public/"
fi

# Persona addon
rsync -a --delete "$SRC/skills/" "$DEST/skills/"
echo "  skills/ ($(find "$DEST/skills" -name SKILL.md | wc -l | tr -d ' ') skills)"

rsync -a "$SRC/persona/" "$DEST/persona/"
echo "  persona/"

rsync -a "$SRC/tools/" "$DEST/tools/"
echo "  tools/"

rsync -a "$SRC/hermes/" "$DEST/hermes/"
echo "  hermes/"

for f in bootstrap.sh bootstrap.ps1 install.sh install.ps1 .env.example .gitignore README.md LICENSE; do
  if [ -f "$SRC/$f" ]; then
    cp "$SRC/$f" "$DEST/$f"
    echo "  $f"
  fi
done

for f in "$SRC"/env.*.example; do
  [ -f "$f" ] || continue
  cp "$f" "$DEST/"
  echo "  $(basename "$f")"
done

rsync -a "$SRC/scripts/" "$DEST/scripts/"
chmod +x "$DEST/scripts/"*.sh "$DEST/tools/"*.py 2>/dev/null || true
echo "  scripts/"

echo ""
echo "Done. Review and commit in $DEST:"
echo "  cd $DEST && git status"