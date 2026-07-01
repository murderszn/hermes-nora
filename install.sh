#!/usr/bin/env bash
set -euo pipefail

REPO="https://github.com/murderszn/hermes-nora.git"
INSTALL_DIR="${NORA_INSTALL_DIR:-$HOME/.nora}"

echo "  ◉  Nora — Hermes Agent Ops Persona"
echo ""

if ! command -v git &>/dev/null; then
  echo "Error: git is required. Install git and retry."
  exit 1
fi

if [ -d "$INSTALL_DIR/.git" ]; then
  echo "Updating existing install at $INSTALL_DIR"
  git -C "$INSTALL_DIR" pull --ff-only
else
  echo "Cloning into $INSTALL_DIR"
  git clone "$REPO" "$INSTALL_DIR"
fi

if [ -f "$INSTALL_DIR/bootstrap.sh" ]; then
  bash "$INSTALL_DIR/bootstrap.sh"
else
  echo ""
  echo "Installed to $INSTALL_DIR"
  echo "Run: cd $INSTALL_DIR"
fi

echo ""
echo "  Nora files are in $INSTALL_DIR"
echo ""
echo "  Next — run the onboarding wizard:"
echo "    $INSTALL_DIR/scripts/onboard.sh"
echo ""
echo "  Or macOS/Linux activate only:"
echo "    $INSTALL_DIR/scripts/activate.sh"
echo ""
echo "  Docs: $INSTALL_DIR/persona/channels.md"