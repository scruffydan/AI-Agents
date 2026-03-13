#!/usr/bin/env bash
# Install opencode.json with secure permission defaults to ~/.config/opencode/

set -eu

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_ROOT/source/opencode.json"
DEST="$HOME/.config/opencode/opencode.json"

[[ ! -f "$SRC" ]] && echo "Error: $SRC not found" && exit 1

if [[ -f "$DEST" ]] && [[ "${1:-}" != "-y" ]]; then
    read -rp "Overwrite $DEST? [y/N]: " c
    [[ "$c" != [yY]* ]] && echo "Aborted." && exit 0
fi

mkdir -p "$(dirname "$DEST")"
cp "$SRC" "$DEST"
echo "Installed: $DEST"
