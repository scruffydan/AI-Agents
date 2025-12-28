#!/bin/bash

# OpenCode configuration initializer
# Copies opencode.json from source/ to ~/.config/opencode/

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_FILE="$REPO_ROOT/source/opencode.json"
OPENCODE_DIR="$HOME/.config/opencode"
CONFIG_FILE="$OPENCODE_DIR/opencode.json"
FORCE=false

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse command-line arguments
show_help() {
    echo "Usage: ./opencode-init.sh [OPTIONS]"
    echo ""
    echo "Copies opencode.json configuration file with secure defaults."
    echo ""
    echo "Options:"
    echo "  -y, --yes      Automatically overwrite existing config"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "Source: $SOURCE_FILE"
    echo "Target: $CONFIG_FILE"
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

# Check source file exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo -e "${RED}Error: Source file not found: $SOURCE_FILE${NC}"
    exit 1
fi

# Check if config already exists
if [ -f "$CONFIG_FILE" ]; then
    if [ "$FORCE" = true ]; then
        echo -e "${YELLOW}Overwriting existing config...${NC}"
    else
        echo -e "${YELLOW}Config already exists: $CONFIG_FILE${NC}"
        read -p "Overwrite? [y/N]: " choice
        case "$choice" in
            y|Y)
                echo "Overwriting..."
                ;;
            *)
                echo "Aborted."
                exit 0
                ;;
        esac
    fi
fi

# Create directory if needed
mkdir -p "$OPENCODE_DIR"

# Copy the config file
cp "$SOURCE_FILE" "$CONFIG_FILE"

echo ""
echo -e "${GREEN}OpenCode config installed!${NC}"
echo ""
echo "Location: $CONFIG_FILE"
echo ""
echo "Configuration summary:"
echo "  - Sharing: disabled"
echo "  - File edits: ask for permission"
echo "  - External directories: ask for permission"
echo "  - Git push/commit: ask for permission"
echo "  - Git read operations: allowed"
echo "  - Destructive commands (rm -rf): denied"
echo "  - Package installs: ask for permission"
echo ""
echo "Edit $CONFIG_FILE to customize further."
echo "Schema reference: https://opencode.ai/config.json"
echo ""
