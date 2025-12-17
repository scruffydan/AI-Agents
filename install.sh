#!/bin/bash

# Installation script for Claude Code AI Agents
# Copies files to ~/.claude/

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
FORCE=false

# Parse command-line arguments
show_help() {
    echo "Usage: ./install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -y, --yes      Automatically answer yes to all prompts (force overwrite)"
    echo "  -h, --help     Show this help message"
    echo ""
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -y|--yes)
            FORCE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

echo "Installing Claude Code AI Agents..."
echo "Repository root: $REPO_ROOT"
echo "Target directory: $CLAUDE_DIR"
if [ "$FORCE" = true ]; then
    echo "Mode: Force overwrite enabled"
fi
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

# Create target directories
echo "Creating directories..."
mkdir -p "$CLAUDE_DIR/agents"
mkdir -p "$CLAUDE_DIR/commands"
mkdir -p "$CLAUDE_DIR/prompts"

# Copy agent files
echo ""
echo "Copying agent files..."
for agent in "$REPO_ROOT/claude/agents/"*.md; do
    if [ -f "$agent" ]; then
        agent_name=$(basename "$agent")
        target="$CLAUDE_DIR/agents/$agent_name"

        # Check if target exists
        if [ -f "$target" ] || [ -L "$target" ]; then
            if [ "$FORCE" = true ]; then
                rm -rf "$target"
            elif ! ask_user_action "$target" "agents/$agent_name"; then
                continue
            fi
        fi

        echo "  Copying: $agent_name"
        cp "$agent" "$target"
    fi
done

# Copy command files
echo ""
echo "Copying command files..."
for command in "$REPO_ROOT/claude/commands/"*.md; do
    if [ -f "$command" ]; then
        command_name=$(basename "$command")
        target="$CLAUDE_DIR/commands/$command_name"

        # Check if target exists
        if [ -f "$target" ] || [ -L "$target" ]; then
            if [ "$FORCE" = true ]; then
                rm -rf "$target"
            elif ! ask_user_action "$target" "commands/$command_name"; then
                continue
            fi
        fi

        echo "  Copying: $command_name"
        cp "$command" "$target"
    fi
done

# Copy prompt files
echo ""
echo "Copying prompt files..."
for prompt in "$REPO_ROOT/claude/prompts/"*.md; do
    if [ -f "$prompt" ]; then
        prompt_name=$(basename "$prompt")
        target="$CLAUDE_DIR/prompts/$prompt_name"

        # Check if target exists
        if [ -f "$target" ] || [ -L "$target" ]; then
            if [ "$FORCE" = true ]; then
                rm -rf "$target"
            elif ! ask_user_action "$target" "prompts/$prompt_name"; then
                continue
            fi
        fi

        echo "  Copying: $prompt_name"
        cp "$prompt" "$target"
    fi
done

# Copy CLAUDE.md
echo ""
echo "Copying CLAUDE.md..."
if [ -f "$CLAUDE_DIR/CLAUDE.md" ] || [ -L "$CLAUDE_DIR/CLAUDE.md" ]; then
    if [ "$FORCE" = true ]; then
        rm -rf "$CLAUDE_DIR/CLAUDE.md"
        cp "$REPO_ROOT/claude/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
    elif ask_user_action "$CLAUDE_DIR/CLAUDE.md" "CLAUDE.md"; then
        cp "$REPO_ROOT/claude/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
    fi
else
    cp "$REPO_ROOT/claude/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
fi

echo ""
echo "✅ Installation complete!"
echo ""
if [ -d "$CLAUDE_DIR/agents" ]; then
    echo "Available agents:"
    ls -1 "$CLAUDE_DIR/agents/" | sed 's/^/  - /'
fi
echo ""
if [ -d "$CLAUDE_DIR/commands" ]; then
    echo "Available commands:"
    ls -1 "$CLAUDE_DIR/commands/" | sed 's/^/  - /'
fi
echo ""
if [ -d "$CLAUDE_DIR/prompts" ]; then
    echo "Prompts installed: $(ls -1 "$CLAUDE_DIR/prompts/" | wc -l | tr -d ' ') files"
fi
echo ""
if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
    echo "Global instructions: $CLAUDE_DIR/CLAUDE.md"
fi
echo ""
echo "Usage:"
echo "  - Agents auto-invoke when Claude detects relevant tasks"
echo "  - Commands: /code-security, /code-readability, /code-performance, /code-full-review"
echo ""
echo "Note: Files are copied (not symlinked). Run ./install.sh again to update."
echo "      Use ./install.sh -y to force overwrite without prompts."
echo ""
