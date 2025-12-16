#!/bin/bash

# Installation script for Claude Code AI Agents
# Creates necessary directories and symlinks to ~/.claude/

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "Installing Claude Code AI Agents..."
echo "Repository root: $REPO_ROOT"
echo "Target directory: $CLAUDE_DIR"
echo ""

# Helper function to ask user what to do with existing file
ask_user_action() {
    local target="$1"
    local name="$2"

    if [ -L "$target" ]; then
        echo "⚠️  Existing symlink found: $name"
        echo "   Current target: $(readlink "$target")"
    elif [ -f "$target" ]; then
        echo "⚠️  Existing file found: $name"
    elif [ -d "$target" ]; then
        echo "⚠️  Existing directory found: $name"
    fi

    read -p "   Overwrite? [y/N]: " choice

    case "$choice" in
        y|Y)
            echo "   Removing existing"
            rm -rf "$target"
            return 0
            ;;
        *)
            echo "   Skipping"
            return 1
            ;;
    esac
}

# Symlink agents directory
echo "Symlinking agents directory..."
if [ -L "$CLAUDE_DIR/agents" ] || [ -d "$CLAUDE_DIR/agents" ]; then
    if ask_user_action "$CLAUDE_DIR/agents" "agents/"; then
        ln -s "$REPO_ROOT/claude/agents" "$CLAUDE_DIR/agents"
    fi
else
    ln -s "$REPO_ROOT/claude/agents" "$CLAUDE_DIR/agents"
fi

# Symlink commands directory
echo ""
echo "Symlinking commands directory..."
if [ -L "$CLAUDE_DIR/commands" ] || [ -d "$CLAUDE_DIR/commands" ]; then
    if ask_user_action "$CLAUDE_DIR/commands" "commands/"; then
        ln -s "$REPO_ROOT/claude/commands" "$CLAUDE_DIR/commands"
    fi
else
    ln -s "$REPO_ROOT/claude/commands" "$CLAUDE_DIR/commands"
fi

# Symlink prompts directory
echo ""
echo "Symlinking prompts directory..."
if [ -L "$CLAUDE_DIR/prompts" ] || [ -d "$CLAUDE_DIR/prompts" ]; then
    if ask_user_action "$CLAUDE_DIR/prompts" "prompts/"; then
        ln -s "$REPO_ROOT/claude/prompts" "$CLAUDE_DIR/prompts"
    fi
else
    ln -s "$REPO_ROOT/claude/prompts" "$CLAUDE_DIR/prompts"
fi

# Symlink CLAUDE.md
echo ""
echo "Symlinking CLAUDE.md..."
if [ -L "$CLAUDE_DIR/CLAUDE.md" ] || [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
    if ask_user_action "$CLAUDE_DIR/CLAUDE.md" "CLAUDE.md"; then
        ln -s "$REPO_ROOT/claude/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
    fi
else
    ln -s "$REPO_ROOT/claude/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
fi

echo ""
echo "✅ Installation complete!"
echo ""
if [ -L "$CLAUDE_DIR/agents" ]; then
    echo "Agents directory: $CLAUDE_DIR/agents/ → $(readlink "$CLAUDE_DIR/agents")"
    echo "  Available agents:"
    ls -1 "$CLAUDE_DIR/agents/" | sed 's/^/    - /'
fi
echo ""
if [ -L "$CLAUDE_DIR/commands" ]; then
    echo "Commands directory: $CLAUDE_DIR/commands/ → $(readlink "$CLAUDE_DIR/commands")"
    echo "  Available commands:"
    ls -1 "$CLAUDE_DIR/commands/" | sed 's/^/    - /'
fi
echo ""
if [ -L "$CLAUDE_DIR/prompts" ]; then
    echo "Prompts directory: $CLAUDE_DIR/prompts/ → $(readlink "$CLAUDE_DIR/prompts")"
fi
echo ""
if [ -L "$CLAUDE_DIR/CLAUDE.md" ]; then
    echo "Global instructions: $CLAUDE_DIR/CLAUDE.md → $(readlink "$CLAUDE_DIR/CLAUDE.md")"
fi
echo ""
echo "Usage:"
echo "  - Agents auto-invoke when Claude detects relevant tasks"
echo "  - Commands: /code-security, /code-readability, /code-performance, /code-full-review"
echo ""
