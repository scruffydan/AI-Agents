#!/usr/bin/env bash

set -eu

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
FORCE=false
WORK=false
PROVIDER=""
HARNESSES=()

usage() {
    echo "Usage: ./install.sh [opencode|claude|codex ...] [OPTIONS]"
    echo
    echo "Options:"
    echo "  --work                       Use work model mappings"
    echo "  --opencode-provider NAME     openai, github-copilot, or opencode"
    echo "  -y, --force                  Replace changed files without prompting"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        opencode|claude|codex)
            HARNESSES+=("$1")
            shift
            ;;
        --work)
            WORK=true
            shift
            ;;
        --opencode-provider)
            [ "$#" -ge 2 ] || { echo "Missing provider name" >&2; exit 2; }
            PROVIDER="$2"
            shift 2
            ;;
        -y|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

[ "${#HARNESSES[@]}" -gt 0 ] || HARNESSES=(opencode claude codex)
: "${HOME:?HOME must be set}"

BUILD_ARGS=("${HARNESSES[@]}")
[ "$WORK" = false ] || BUILD_ARGS+=(--work)
[ -z "$PROVIDER" ] || BUILD_ARGS+=(--opencode-provider "$PROVIDER")
"$PYTHON" "$ROOT/build.py" "${BUILD_ARGS[@]}"

# Replaced files are moved here instead of deleted, mirroring their path under $HOME.
BACKUP_DIR="$HOME/.ai-agents-backups/$(date +%Y%m%d-%H%M%S)"

install_item() {
    source_path="$1"
    destination="$2"

    if [ -e "$destination" ] || [ -L "$destination" ]; then
        if diff -rq "$source_path" "$destination" >/dev/null 2>&1; then
            return
        fi
        if [ "$FORCE" = false ]; then
            printf "Replace %s? [y/N]: " "$destination"
            read -r answer
            case "$answer" in
                y|Y|yes|YES) ;;
                *) echo "Skipped: $destination"; return ;;
            esac
        fi
        backup="$BACKUP_DIR/${destination#"$HOME"/}"
        mkdir -p "$(dirname "$backup")"
        mv -- "$destination" "$backup"
        echo "Backed up: $destination -> $backup"
    fi

    mkdir -p "$(dirname "$destination")"
    cp -R "$source_path" "$destination"
    echo "Installed: $destination"
}

# Install each generated entry separately so unrelated agents and skills in a
# shared directory are left alone.
install_entries() {
    source_dir="$1"
    destination_dir="$2"

    for entry in "$source_dir"/*; do
        [ -e "$entry" ] || continue
        install_item "$entry" "$destination_dir/$(basename "$entry")"
    done
}

for harness in "${HARNESSES[@]}"; do
    case "$harness" in
        opencode)
            target="$HOME/.config/opencode"
            install_item "$ROOT/build/opencode/AGENTS.md" "$target/AGENTS.md"
            install_entries "$ROOT/build/opencode/agents" "$target/agents"
            install_entries "$ROOT/build/opencode/commands" "$target/commands"
            install_entries "$ROOT/build/opencode/skills" "$target/skills"
            ;;
        claude)
            target="$HOME/.claude"
            install_item "$ROOT/build/claude/CLAUDE.md" "$target/CLAUDE.md"
            install_entries "$ROOT/build/claude/agents" "$target/agents"
            install_entries "$ROOT/build/claude/skills" "$target/skills"
            ;;
        codex)
            install_item "$ROOT/build/codex/AGENTS.md" "$HOME/.codex/AGENTS.md"
            install_entries "$ROOT/build/codex/.codex/agents" "$HOME/.codex/agents"
            install_entries "$ROOT/build/codex/.agents/skills" "$HOME/.agents/skills"
            ;;
    esac
done
