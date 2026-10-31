#!/usr/bin/env bash
# Install opencode.json with secure permission defaults to ~/.config/opencode/

set -eu
umask 077

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_ROOT/source/opencode.json"
DEST="$HOME/.config/opencode/opencode.json"
YES=false

usage() {
    echo "Usage: $(basename "$0") [-y|--yes]"
    echo "  -y, --yes   Replace an existing $DEST without prompting (backs up first)"
    echo "This replaces the entire config; merge source/opencode.json manually to retain local settings."
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

if [[ -L "$DEST" ]]; then
    echo "Error: refusing to overwrite symlink target $DEST"
    exit 1
fi

if [[ -e "$DEST" ]] && [[ ! -f "$DEST" ]]; then
    echo "Error: $DEST is not a regular file" >&2
    exit 1
fi

if [[ -f "$DEST" ]] && cmp -s "$SRC" "$DEST"; then
    chmod 600 "$DEST"
    echo "Unchanged: $DEST"
    exit 0
fi

if [[ -f "$DEST" ]] && [[ "$YES" != true ]]; then
    if ! read -rp "Replace entire $DEST (backup first)? [y/N]: " answer; then
        echo "Aborted: no confirmation received."
        exit 1
    fi
    case "$answer" in
        y|Y|yes|YES) ;;
        *) echo "Aborted."; exit 0 ;;
    esac
fi

if [[ -f "$DEST" ]]; then
    mkdir -p "$HOME/.ai-agents-backups"
    BACKUP_DIR="$(mktemp -d "$HOME/.ai-agents-backups/opencode-$(date +%Y%m%d-%H%M%S)-XXXXXX")"
    install -m 600 "$DEST" "$BACKUP_DIR/opencode.json"
    echo "Backed up: $DEST -> $BACKUP_DIR/opencode.json"
fi

mkdir -p "$(dirname "$DEST")"
install -m 600 "$SRC" "$DEST"
echo "Installed: $DEST"
