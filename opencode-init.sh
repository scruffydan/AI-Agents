#!/usr/bin/env bash
# Install opencode.json with secure permission defaults to ~/.config/opencode/

set -eu

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_ROOT/source/opencode.json"
DEST="$HOME/.config/opencode/opencode.json"
YES=false

usage() {
    echo "Usage: $(basename "$0") [-y|--yes]"
    echo "  -y, --yes   Overwrite an existing $DEST without prompting"
}

for arg in "$@"; do
    case "$arg" in
        -y|--yes) YES=true ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Error: unknown option: $arg" >&2; usage >&2; exit 1 ;;
    esac
done

if [[ ! -f "$SRC" ]]; then
    echo "Error: $SRC not found"
    exit 1
fi

if [[ -f "$DEST" ]] && [[ "$YES" != true ]]; then
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
