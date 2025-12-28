#!/bin/bash

# Installation script for AI Agents
# Supports Claude Code and OpenCode
# Installs from build/ directory (run build.sh first or use this script)

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$REPO_ROOT/build"
CLAUDE_DIR="$HOME/.claude"
OPENCODE_DIR="$HOME/.config/opencode"
FORCE=false
INSTALL_CLAUDE=false
INSTALL_OPENCODE=false
TARGET_SPECIFIED=false

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse command-line arguments
show_help() {
    echo "Usage: ./install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -y, --yes          Automatically answer yes to all prompts (force overwrite)"
    echo "  --claude           Install Claude Code configs"
    echo "  --opencode         Install OpenCode configs"
    echo "  --all              Install both Claude Code and OpenCode (default if no target specified)"
    echo "  --skip-build       Skip running build.sh (use existing build/)"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./install.sh                    # Interactive: prompts which to install"
    echo "  ./install.sh --claude           # Install only Claude Code"
    echo "  ./install.sh --opencode         # Install only OpenCode"
    echo "  ./install.sh --all              # Install both without prompting"
    echo "  ./install.sh --claude -y        # Install Claude Code, force overwrite"
    echo ""
}

SKIP_BUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -y|--yes)
            FORCE=true
            shift
            ;;
        --claude)
            INSTALL_CLAUDE=true
            TARGET_SPECIFIED=true
            shift
            ;;
        --opencode)
            INSTALL_OPENCODE=true
            TARGET_SPECIFIED=true
            shift
            ;;
        --all)
            INSTALL_CLAUDE=true
            INSTALL_OPENCODE=true
            TARGET_SPECIFIED=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
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

# Interactive selection if no target specified
if [ "$TARGET_SPECIFIED" = false ]; then
    echo -e "${YELLOW}Select what to install:${NC}"
    echo "  1) Claude Code only"
    echo "  2) OpenCode only"
    echo "  3) Both (default)"
    echo ""
    read -p "Choice [1/2/3]: " choice
    
    case "$choice" in
        1)
            INSTALL_CLAUDE=true
            ;;
        2)
            INSTALL_OPENCODE=true
            ;;
        *)
            INSTALL_CLAUDE=true
            INSTALL_OPENCODE=true
            ;;
    esac
    echo ""
fi

# Run build.sh first
if [ "$SKIP_BUILD" = false ]; then
    echo -e "${YELLOW}Running build.sh...${NC}"
    "$REPO_ROOT/build.sh"
    echo ""
fi

# Verify build directory exists
if [ ! -d "$BUILD_DIR" ]; then
    echo -e "${RED}Error: build/ directory not found. Run ./build.sh first.${NC}"
    exit 1
fi

echo -e "${GREEN}Installing AI Agents...${NC}"
echo "Build directory: $BUILD_DIR"
if [ "$INSTALL_CLAUDE" = true ]; then
    echo "Claude target: $CLAUDE_DIR"
fi
if [ "$INSTALL_OPENCODE" = true ]; then
    echo "OpenCode target: $OPENCODE_DIR"
fi
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
            [[ -n "$target" ]] && rm -rf "$target"
            return 0
            ;;
        *)
            echo "   Skipping"
            return 1
            ;;
    esac
}

# Copy a single file with overwrite handling
# Returns 0 if copied, 1 if skipped
copy_with_overwrite() {
    local src="$1"
    local dest="$2"
    local label="$3"
    
    if [ -f "$dest" ] || [ -L "$dest" ]; then
        if [ "$FORCE" = true ]; then
            [[ -n "$dest" ]] && rm -rf "$dest"
        elif ! ask_user_action "$dest" "$label"; then
            return 1
        fi
    fi
    
    cp "$src" "$dest"
    echo "  Copied: $label"
    return 0
}

# Copy all .md files from src_dir to dest_dir
copy_files() {
    local src_dir="$1"
    local dest_dir="$2"
    local label="$3"
    
    [ ! -d "$src_dir" ] && return
    mkdir -p "$dest_dir"
    
    for file in "$src_dir"/*.md; do
        [ -f "$file" ] || continue
        copy_with_overwrite "$file" "$dest_dir/$(basename "$file")" "$label/$(basename "$file")"
    done
}

# Copy a single file to destination
copy_file() {
    local src="$1"
    local dest="$2"
    local label="$3"
    
    [ ! -f "$src" ] && return
    mkdir -p "$(dirname "$dest")"
    copy_with_overwrite "$src" "$dest" "$label"
}

# ============================================================
# CLAUDE CODE INSTALLATION
# ============================================================
if [ "$INSTALL_CLAUDE" = true ]; then
    echo -e "${YELLOW}Installing Claude Code configs...${NC}"
    
    # Create target directories
    mkdir -p "$CLAUDE_DIR/agents"
    mkdir -p "$CLAUDE_DIR/commands"
    
    # Copy agent files
    echo ""
    echo "Copying agent files..."
    copy_files "$BUILD_DIR/claude/agents" "$CLAUDE_DIR/agents" "agents"
    
    # Copy command files
    echo ""
    echo "Copying command files..."
    copy_files "$BUILD_DIR/claude/commands" "$CLAUDE_DIR/commands" "commands"
    
    # Copy CLAUDE.md
    echo ""
    echo "Copying CLAUDE.md..."
    copy_file "$BUILD_DIR/claude/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md" "CLAUDE.md"
    
    echo ""
    echo -e "${GREEN}Claude Code installation complete!${NC}"
    echo ""
    if [ -d "$CLAUDE_DIR/agents" ]; then
        echo "Available agents:"
        ls -1 "$CLAUDE_DIR/agents/" 2>/dev/null | sed 's/^/  - /' || echo "  (none)"
    fi
    echo ""
    if [ -d "$CLAUDE_DIR/commands" ]; then
        echo "Available commands:"
        ls -1 "$CLAUDE_DIR/commands/" 2>/dev/null | sed 's/^/  - /' || echo "  (none)"
    fi
    echo ""
    if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        echo "Global instructions: $CLAUDE_DIR/CLAUDE.md"
    fi
fi

# ============================================================
# OPENCODE INSTALLATION
# ============================================================
if [ "$INSTALL_OPENCODE" = true ]; then
    echo ""
    echo -e "${YELLOW}Installing OpenCode configs...${NC}"
    
    # Create target directories
    mkdir -p "$OPENCODE_DIR/agent"
    
    # Copy agent files
    echo ""
    echo "Copying agent files..."
    copy_files "$BUILD_DIR/opencode/agent" "$OPENCODE_DIR/agent" "agent"
    
    # Copy command files (if any exist)
    if [ -d "$BUILD_DIR/opencode/command" ] && [ "$(ls -A "$BUILD_DIR/opencode/command" 2>/dev/null)" ]; then
        mkdir -p "$OPENCODE_DIR/command"
        echo ""
        echo "Copying command files..."
        copy_files "$BUILD_DIR/opencode/command" "$OPENCODE_DIR/command" "command"
    fi
    
    # Copy mode files (if any exist)
    if [ -d "$BUILD_DIR/opencode/mode" ] && [ "$(ls -A "$BUILD_DIR/opencode/mode" 2>/dev/null)" ]; then
        mkdir -p "$OPENCODE_DIR/mode"
        echo ""
        echo "Copying mode files..."
        copy_files "$BUILD_DIR/opencode/mode" "$OPENCODE_DIR/mode" "mode"
    fi
    
    # Copy AGENTS.md
    echo ""
    echo "Copying AGENTS.md..."
    copy_file "$BUILD_DIR/opencode/AGENTS.md" "$OPENCODE_DIR/AGENTS.md" "AGENTS.md"
    
    echo ""
    echo -e "${GREEN}OpenCode installation complete!${NC}"
    echo ""
    if [ -d "$OPENCODE_DIR/agent" ]; then
        echo "Available agents (invoke with @name):"
        ls -1 "$OPENCODE_DIR/agent/" 2>/dev/null | sed 's/\.md$//' | sed 's/^/  @/' || echo "  (none)"
    fi
    if [ -d "$OPENCODE_DIR/command" ] && [ "$(ls -A "$OPENCODE_DIR/command" 2>/dev/null)" ]; then
        echo ""
        echo "Available commands:"
        ls -1 "$OPENCODE_DIR/command/" 2>/dev/null | sed 's/\.md$//' | sed 's/^/  \//' || echo "  (none)"
    fi
    if [ -d "$OPENCODE_DIR/mode" ] && [ "$(ls -A "$OPENCODE_DIR/mode" 2>/dev/null)" ]; then
        echo ""
        echo "Available modes (switch with Tab):"
        ls -1 "$OPENCODE_DIR/mode/" 2>/dev/null | sed 's/\.md$//' | sed 's/^/  /' || echo "  (none)"
    fi
    echo ""
    if [ -f "$OPENCODE_DIR/AGENTS.md" ]; then
        echo "Global instructions: $OPENCODE_DIR/AGENTS.md"
    fi
fi

# ============================================================
# USAGE SUMMARY
# ============================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Installation complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Usage:"
if [ "$INSTALL_CLAUDE" = true ]; then
    echo "  Claude Code:"
    echo "    - Agents auto-invoke when Claude detects relevant tasks"
    echo "    - Commands: /code-security, /code-readability, /code-performance, /code-full-review"
fi
if [ "$INSTALL_OPENCODE" = true ]; then
    echo "  OpenCode:"
    echo "    - Agents: @code-security, @code-readability, @code-performance"
    echo "    - Command: /code-full-review (orchestrates all 3 agents)"
    echo "    - Modes: Switch with Tab key (e.g., brainstorm)"
fi
echo ""
echo "Note: Files are copied (not symlinked). Run ./install.sh again to update."
echo "      Use ./install.sh -y to force overwrite without prompts."
echo ""
