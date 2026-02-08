#!/usr/bin/env bash

# Installation script for AI Agents
# Supports Claude Code and OpenCode
# Installs from build/ directory (run build.sh first or use this script)

set -eu

# Validate HOME is set (defensive programming)
[ -z "$HOME" ] && { echo "Error: HOME environment variable is not set"; exit 1; }

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
    echo "  --vertex           Use Google Vertex AI as the model provider for OpenCode"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./install.sh                    # Interactive: prompts which to install"
    echo "  ./install.sh --claude           # Install only Claude Code"
    echo "  ./install.sh --opencode         # Install only OpenCode"
    echo "  ./install.sh --opencode --vertex # Install OpenCode with Vertex AI models"
    echo "  ./install.sh --all              # Install both without prompting"
    echo "  ./install.sh --claude -y        # Install Claude Code, force overwrite"
    echo ""
}

SKIP_BUILD=false
USE_VERTEX=false

while [ $# -gt 0 ]; do
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
        --vertex)
            USE_VERTEX=true
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

# Check for yq dependency (only if not skipping build)
if [ "$SKIP_BUILD" = false ]; then
    if ! command -v yq &> /dev/null; then
        echo -e "${RED}Error: yq is required but not installed.${NC}"
        echo "Install with: brew install yq"
        echo ""
        echo "Alternatively, run with --skip-build if you already have the build/ directory:"
        echo "  ./install.sh --skip-build"
        exit 1
    fi
fi

# Run build.sh first
if [ "$SKIP_BUILD" = false ]; then
    echo -e "${YELLOW}Running build.sh...${NC}"
    if [ "$USE_VERTEX" = true ]; then
        "$REPO_ROOT/build.sh" --vertex
    else
        "$REPO_ROOT/build.sh"
    fi
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
    if [ "$USE_VERTEX" = true ]; then
        echo "OpenCode provider: Google Vertex AI"
    else
        echo "OpenCode provider: OpenCode"
    fi
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
            [ -n "$target" ] && rm -rf -- "$target"
            return 0
            ;;
        *)
            echo "   Skipping"
            return 1
            ;;
    esac
}

# Copy a file or directory with overwrite handling
# Returns 0 if copied, 1 if skipped
copy_with_overwrite() {
    local src="$1"
    local dest="$2"
    local label="$3"
    
    # Skip if source doesn't exist
    [ ! -e "$src" ] && return 1
    
    # Handle existing destination
    if [ -e "$dest" ] || [ -L "$dest" ]; then
        if [ "$FORCE" = true ]; then
            [ -n "$dest" ] && rm -rf -- "$dest"
        elif ! ask_user_action "$dest" "$label"; then
            return 1
        fi
    fi
    
    # Ensure parent directory exists
    mkdir -p "$(dirname "$dest")"
    
    # Copy (use -R for directories)
    if [ -d "$src" ]; then
        cp -R -- "$src" "$dest"
    else
        cp -- "$src" "$dest"
    fi
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
    
    local count=0
    for file in "$src_dir"/*.md; do
        [ -f "$file" ] || continue
        if copy_with_overwrite "$file" "$dest_dir/$(basename "$file")" "$label/$(basename "$file")"; then
            ((count++))
        fi
    done
    
    echo "  Total copied: $count file(s)"
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

# Copy skill directories (each skill is its own directory)
copy_skill_dirs() {
    local src_dir="$1"
    local dest_dir="$2"
    local label="$3"

    [ ! -d "$src_dir" ] && return
    mkdir -p "$dest_dir"

    local count=0
    for dir in "$src_dir"/*; do
        [ -d "$dir" ] || continue
        if copy_with_overwrite "$dir" "$dest_dir/$(basename "$dir")" "$label/$(basename "$dir")"; then
            ((count++))
        fi
    done
    
    echo "  Total copied: $count skill(s)"
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
    echo "Copying base instructions..."
    copy_file "$BUILD_DIR/claude/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md" "CLAUDE.md"

    # Copy skills
    if [ -d "$BUILD_DIR/claude/skills" ]; then
        echo ""
        echo "Copying skills..."
        copy_skill_dirs "$BUILD_DIR/claude/skills" "$CLAUDE_DIR/skills" "skills"
    fi
    
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Claude Code installation complete!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    if [ -d "$CLAUDE_DIR/agents" ]; then
        agent_count=$(ls -1 "$CLAUDE_DIR/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')
        echo "Available agents ($agent_count):"
        ls -1 "$CLAUDE_DIR/agents/"*.md 2>/dev/null | sed 's|.*/||; s/\.md$//' | sed 's/^/  - /' || echo "  (none)"
    fi
    echo ""
    if [ -d "$CLAUDE_DIR/commands" ]; then
        command_count=$(ls -1 "$CLAUDE_DIR/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')
        echo "Available commands ($command_count):"
        ls -1 "$CLAUDE_DIR/commands/"*.md 2>/dev/null | sed 's|.*/||; s/\.md$//' | sed 's/^/  - /' || echo "  (none)"
    fi
    echo ""
    if [ -d "$CLAUDE_DIR/skills" ]; then
        skill_count=$(find "$CLAUDE_DIR/skills" -type d -mindepth 1 -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')
        echo "Available skills ($skill_count):"
        ls -1 "$CLAUDE_DIR/skills/" 2>/dev/null | sed 's/^/  - /' || echo "  (none)"
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
    
    # Copy AGENTS.md
    echo ""
    echo "Copying base instructions..."
    copy_file "$BUILD_DIR/opencode/AGENTS.md" "$OPENCODE_DIR/AGENTS.md" "AGENTS.md"

    # Copy skills
    if [ -d "$BUILD_DIR/opencode/skill" ]; then
        echo ""
        echo "Copying skills..."
        copy_skill_dirs "$BUILD_DIR/opencode/skill" "$OPENCODE_DIR/skill" "skill"
    fi
    
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}OpenCode installation complete!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    if [ -d "$OPENCODE_DIR/agent" ]; then
        agent_count=$(ls -1 "$OPENCODE_DIR/agent/"*.md 2>/dev/null | wc -l | tr -d ' ')
        echo "Available agents ($agent_count) - invoke with @name:"
        ls -1 "$OPENCODE_DIR/agent/"*.md 2>/dev/null | sed 's|.*/||; s/\.md$//' | sed 's/^/  @/' || echo "  (none)"
    fi
    if [ -d "$OPENCODE_DIR/command" ] && [ "$(ls -A "$OPENCODE_DIR/command" 2>/dev/null)" ]; then
        echo ""
        command_count=$(ls -1 "$OPENCODE_DIR/command/"*.md 2>/dev/null | wc -l | tr -d ' ')
        echo "Available commands ($command_count) - invoke with /name:"
        ls -1 "$OPENCODE_DIR/command/"*.md 2>/dev/null | sed 's|.*/||; s/\.md$//' | sed 's/^/  /' || echo "  (none)"
    fi
    if [ -d "$OPENCODE_DIR/skill" ]; then
        echo ""
        skill_count=$(find "$OPENCODE_DIR/skill" -type d -mindepth 1 -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')
        echo "Available skills ($skill_count):"
        ls -1 "$OPENCODE_DIR/skill/" 2>/dev/null | sed 's/^/  - /' || echo "  (none)"
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
echo -e "${GREEN}All installations complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Quick Start:"
if [ "$INSTALL_CLAUDE" = true ]; then
    echo ""
    echo "  Claude Code:"
    echo "    • Agents auto-invoke when Claude detects relevant tasks"
    echo "    • Slash commands: /code-full-review (orchestrates all specialist agents)"
    echo "    • Config location: $CLAUDE_DIR"
fi
if [ "$INSTALL_OPENCODE" = true ]; then
    echo ""
    echo "  OpenCode:"
    echo "    • Specialist agents: @code-security, @code-readability, @code-performance,"
    echo "      @code-redundancy, @code-simplifier"
    echo "    • Utility agents: @explore, @sidebar, @docs-fetcher, @git-commit"
    echo "    • Primary modes (Tab to switch): brainstorm, thorough-plan"
    echo "    • Slash commands: /code-full-review (orchestrates all 5 specialist agents)"
    echo "    • Config location: $OPENCODE_DIR"
fi
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check for unmapped models in source prompts
MODEL_MAPPINGS_FILE="$REPO_ROOT/source/model-mappings.json"
UNMAPPED_MODELS=""

if [ -f "$MODEL_MAPPINGS_FILE" ] && [ -d "$REPO_ROOT/source/prompts" ]; then
    for prompt_file in "$REPO_ROOT/source/prompts"/*.md; do
        [ -f "$prompt_file" ] || continue
        # Extract model from opencode section
        model=$(sed -n '/^opencode:/,/^---$/p' "$prompt_file" 2>/dev/null | grep "^  model:" | head -1 | sed 's/.*model: //')
        if [ -n "$model" ] && echo "$model" | grep -q "^opencode/"; then
            # Check if model is in mappings
            if ! jq -e --arg m "$model" '.models[$m] // empty' "$MODEL_MAPPINGS_FILE" >/dev/null 2>&1; then
                if [ -z "$UNMAPPED_MODELS" ]; then
                    UNMAPPED_MODELS="$model"
                else
                    UNMAPPED_MODELS="$UNMAPPED_MODELS
$model"
                fi
            fi
        fi
    done
fi

if [ -n "$UNMAPPED_MODELS" ]; then
    echo -e "${YELLOW}⚠ Warning: The following models were not mapped in source/model-mappings.json:${NC}"
    echo "$UNMAPPED_MODELS" | sort -u | sed 's/^/  - /'
    echo ""
    echo "These models will use their original opencode/ provider."
    echo "Add mappings to source/model-mappings.json if needed."
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

echo "Notes:"
echo "  • Files are copied (not symlinked). Run ./install.sh again to update."
echo "  • Use ./install.sh -y to force overwrite without prompts."
echo "  • Use ./install.sh --help to see all installation options."
echo ""
