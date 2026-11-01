#!/usr/bin/env bash

set -eu

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
FORCE=false
ALL=false
WORK=false
PROVIDER=""
HARNESSES=()

usage() {
    echo "Usage: ./install.sh [codex|claude|opencode ...] [OPTIONS]"
    echo
    echo "With no harness arguments, prompts for a selection (default: codex)."
    echo
    echo "Options:"
    echo "  --all                        Install Codex, Claude Code, and OpenCode"
    echo "  --work                       Use work model mappings"
    echo "  --opencode-provider NAME     openai or opencode"
    echo "  -y, --force                  Replace changed files without prompting"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        codex|claude|opencode)
            HARNESSES+=("$1")
            shift
            ;;
        --all)
            ALL=true
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

if [ "$ALL" = true ]; then
    if [ "${#HARNESSES[@]}" -gt 0 ]; then
        echo "Use --all or explicit harness names, not both." >&2
        exit 2
    fi
    HARNESSES=(codex claude opencode)
elif [ "${#HARNESSES[@]}" -eq 0 ]; then
    echo "Which harnesses would you like to install?"
    echo "  1) Codex (default)"
    echo "  2) Claude Code"
    echo "  3) OpenCode"
    while true; do
        printf "Enter numbers or names separated by spaces [1]: "
        if ! read -r -a selections; then
            echo "No selection received. Pass harness names or --all for unattended installs." >&2
            exit 2
        fi
        [ "${#selections[@]}" -gt 0 ] || selections=(codex)
        HARNESSES=()
        valid=true
        for selection in "${selections[@]}"; do
            case "$selection" in
                1|codex) selected=codex ;;
                2|claude) selected=claude ;;
                3|opencode) selected=opencode ;;
                *)
                    echo "Invalid selection: $selection. Choose 1, 2, 3, codex, claude, or opencode." >&2
                    valid=false
                    break
                    ;;
            esac
            case " ${HARNESSES[*]:-} " in
                *" $selected "*) ;;
                *) HARNESSES+=("$selected") ;;
            esac
        done
        [ "$valid" = false ] || break
    done
fi
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

# Retire only known renamed skills after their replacement was installed. Keep
# local edits recoverable, and leave old entries alone if replacement was skipped.
retire_skill() {
    local old="$1" replacement="$2" generated="$3"
    [ -e "$old" ] || [ -L "$old" ] || return 0
    diff -rq "$generated" "$replacement" >/dev/null 2>&1 || return 0
    if [ "$FORCE" = false ]; then
        printf "Back up retired skill %s (replaced by %s)? [y/N]: " "$old" "$replacement"
        local answer
        read -r answer || answer=n
        case "$answer" in
            y|Y|yes|YES) ;;
            *) echo "Skipped: $old"; return ;;
        esac
    fi
    local backup="$BACKUP_DIR/${old#"$HOME"/}"
    mkdir -p "$(dirname "$backup")"
    mv -- "$old" "$backup"
    echo "Backed up: $old -> $backup"
}

retire_skills() {
    local generated="$1" installed="$2" legacy_review="$3" old
    for old in using-code-review "$legacy_review"; do
        retire_skill "$installed/$old" "$installed/code-review" "$generated/code-review"
    done
    retire_skill "$installed/mode-brainstorm" "$installed/brainstorm-with-agent" \
        "$generated/brainstorm-with-agent"
}

for harness in "${HARNESSES[@]}"; do
    case "$harness" in
        codex)
            install_item "$ROOT/build/codex/AGENTS.md" "$HOME/.codex/AGENTS.md"
            install_entries "$ROOT/build/codex/.codex/agents" "$HOME/.codex/agents"
            skills_source="$ROOT/build/codex/.agents/skills"
            skills_target="$HOME/.agents/skills"
            legacy_review=command-code-full-review
            ;;
        claude)
            target="$HOME/.claude"
            install_item "$ROOT/build/claude/CLAUDE.md" "$target/CLAUDE.md"
            install_entries "$ROOT/build/claude/agents" "$target/agents"
            skills_source="$ROOT/build/claude/skills"
            skills_target="$target/skills"
            legacy_review=code-full-review
            ;;
        opencode)
            target="$HOME/.config/opencode"
            install_item "$ROOT/build/opencode/AGENTS.md" "$target/AGENTS.md"
            install_entries "$ROOT/build/opencode/agents" "$target/agents"
            install_entries "$ROOT/build/opencode/commands" "$target/commands"
            skills_source="$ROOT/build/opencode/skills"
            skills_target="$target/skills"
            legacy_review=command-code-full-review
            ;;
    esac
    install_entries "$skills_source" "$skills_target"
    retire_skills "$skills_source" "$skills_target" "$legacy_review"
    if [ "$harness" = opencode ] &&
        diff -rq "$skills_source/code-review" "$skills_target/code-review" >/dev/null 2>&1; then
        rm -f -- "$HOME/.config/opencode/commands/code-full-review.md"
    fi
done
