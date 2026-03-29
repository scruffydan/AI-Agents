#!/usr/bin/env bash
# Install opencode.json with secure permission defaults to ~/.config/opencode/

set -eu

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_ROOT/source/opencode.json"
DEST="$HOME/.config/opencode/opencode.json"

if [[ ! -f "$SRC" ]]; then
    echo "Error: $SRC not found"
    exit 1
fi

if [[ -f "$DEST" ]] && [[ "${1:-}" != "-y" ]]; then
    read -rp "Overwrite $DEST? [y/N]: " answer
    if [[ "$answer" != [yY]* ]]; then
        echo "Aborted."
        exit 0
    fi
fi

if [[ -L "$DEST" ]]; then
    echo "Error: refusing to overwrite symlink target $DEST"
    exit 1
fi

mkdir -p "$(dirname "$DEST")"
install -m 600 "$SRC" "$DEST"
echo "Installed: $DEST"
