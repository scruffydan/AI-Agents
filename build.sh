#!/usr/bin/env bash

# Build script for AI-Agents
# Generates Claude Code and OpenCode configs from shared prompts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_DIR="$SCRIPT_DIR/shared/prompts"
BUILD_DIR="$SCRIPT_DIR/build"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building AI-Agents configs...${NC}"
echo "Source: $SHARED_DIR"
echo "Output: $BUILD_DIR"
echo ""

# Clean and create build directories
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/claude/agents"
mkdir -p "$BUILD_DIR/claude/commands"
mkdir -p "$BUILD_DIR/opencode/agent"
mkdir -p "$BUILD_DIR/opencode/command"
mkdir -p "$BUILD_DIR/opencode/rules"

# Function to extract YAML value from frontmatter
# Usage: get_yaml_value "$frontmatter" "key"
get_yaml_value() {
    local content="$1"
    local key="$2"
    echo "$content" | grep -E "^${key}:" | head -1 | sed "s/^${key}:[[:space:]]*//"
}

# Function to extract nested YAML value
# Usage: get_nested_yaml "$frontmatter" "parent" "child"
get_nested_yaml() {
    local content="$1"
    local parent="$2"
    local child="$3"
    echo "$content" | awk -v parent="$parent" -v child="$child" '
        $0 ~ "^"parent":" { in_parent=1; next }
        in_parent && /^[a-z]/ { in_parent=0 }
        in_parent && $0 ~ "^  "child":" { 
            sub(/^  '"$child"':[[:space:]]*/, ""); 
            print; 
            exit 
        }
    '
}

# Function to extract Claude tools (handles "tools: Read, Glob, Grep" format)
get_claude_tools() {
    local content="$1"
    echo "$content" | awk '
        /^claude:/ { in_claude=1; next }
        in_claude && /^[a-z]/ { in_claude=0 }
        in_claude && /^  tools:/ { 
            sub(/^  tools:[[:space:]]*/, ""); 
            print; 
            exit 
        }
    '
}

# Function to extract Claude model
get_claude_model() {
    local content="$1"
    echo "$content" | awk '
        /^claude:/ { in_claude=1; next }
        in_claude && /^[a-z]/ { in_claude=0 }
        in_claude && /^  model:/ { 
            sub(/^  model:[[:space:]]*/, ""); 
            print; 
            exit 
        }
    '
}

# Function to extract OpenCode config block
get_opencode_block() {
    local content="$1"
    echo "$content" | awk '
        /^opencode:/ { in_oc=1; next }
        in_oc && /^[a-z]/ { exit }
        in_oc { print }
    '
}

# Function to check if type includes "agent"
has_agent() {
    local type="$1"
    [[ "$type" == *"agent"* ]]
}

# Function to check if type is command-only
is_command_only() {
    local type="$1"
    [[ "$type" == "command-only" ]]
}

# Process each prompt file
for prompt_file in "$SHARED_DIR"/*.md; do
    filename=$(basename "$prompt_file" .md)
    
    # Skip base-instructions (handled separately)
    if [ "$filename" = "base-instructions" ]; then
        continue
    fi
    
    echo -e "${YELLOW}Processing:${NC} $filename"
    
    # Read the file
    file_content=$(cat "$prompt_file")
    
    # Extract frontmatter (between first two ---)
    frontmatter=$(echo "$file_content" | awk '/^---$/{p=!p; if(p) next; else exit} p')
    
    # Extract content (everything after the second ---)
    content=$(echo "$file_content" | awk 'BEGIN{p=0} /^---$/{p++; if(p==2) {getline; p=3}} p==3{print}')
    
    # Get common values
    description=$(get_yaml_value "$frontmatter" "description")
    type=$(get_yaml_value "$frontmatter" "type")
    
    # Get Claude-specific values
    claude_tools=$(get_claude_tools "$frontmatter")
    claude_model=$(get_claude_model "$frontmatter")
    
    # Get OpenCode-specific values
    opencode_block=$(get_opencode_block "$frontmatter")
    opencode_mode=$(echo "$opencode_block" | grep -E "^  mode:" | sed 's/^  mode:[[:space:]]*//')
    opencode_model=$(echo "$opencode_block" | grep -E "^  model:" | sed 's/^  model:[[:space:]]*//')
    opencode_subtask=$(echo "$opencode_block" | grep -E "^  subtask:" | sed 's/^  subtask:[[:space:]]*//')
    
    # Extract OpenCode tools block
    opencode_tools=$(echo "$opencode_block" | awk '
        /^  tools:/ { in_tools=1; next }
        in_tools && /^  [a-z]/ && !/^    / { exit }
        in_tools { print }
    ')
    
    # === Generate Claude Files ===
    
    # Claude Agent (if type includes "agent")
    if has_agent "$type"; then
        claude_agent_file="$BUILD_DIR/claude/agents/$filename.md"
        {
            echo "---"
            echo "name: $filename"
            echo "description: $description"
            [ -n "$claude_tools" ] && echo "tools: $claude_tools"
            [ -n "$claude_model" ] && echo "model: $claude_model"
            echo "---"
            echo ""
            echo "$content"
        } > "$claude_agent_file"
        echo "  Created: claude/agents/$filename.md"
    fi
    
    # Claude Command (always created)
    claude_command_file="$BUILD_DIR/claude/commands/$filename.md"
    echo "$content" > "$claude_command_file"
    echo "  Created: claude/commands/$filename.md"
    
    # === Generate OpenCode Files ===
    
    # OpenCode Agent (if type includes "agent")
    if has_agent "$type"; then
        opencode_agent_file="$BUILD_DIR/opencode/agent/$filename.md"
        {
            echo "---"
            echo "description: $description"
            [ -n "$opencode_mode" ] && echo "mode: $opencode_mode"
            [ -n "$opencode_model" ] && echo "model: $opencode_model"
            if [ -n "$opencode_tools" ]; then
                echo "tools:"
                echo "$opencode_tools"
            fi
            echo "---"
            echo ""
            echo "$content"
        } > "$opencode_agent_file"
        echo "  Created: opencode/agent/$filename.md"
    fi
    
    # OpenCode Command (always created)
    opencode_command_file="$BUILD_DIR/opencode/command/$filename.md"
    {
        echo "---"
        echo "description: $description"
        if has_agent "$type"; then
            echo "agent: $filename"
        fi
        [ -n "$opencode_subtask" ] && echo "subtask: $opencode_subtask"
        [ -n "$opencode_model" ] && ! has_agent "$type" && echo "model: $opencode_model"
        echo "---"
        echo ""
        if has_agent "$type"; then
            echo "\$ARGUMENTS"
        else
            echo "$content"
        fi
    } > "$opencode_command_file"
    echo "  Created: opencode/command/$filename.md"
    
    echo ""
done

# Generate CLAUDE.md from base-instructions.md
echo -e "${YELLOW}Generating:${NC} CLAUDE.md"
if [ -f "$SHARED_DIR/base-instructions.md" ]; then
    cp "$SHARED_DIR/base-instructions.md" "$BUILD_DIR/claude/CLAUDE.md"
    echo "  Created: claude/CLAUDE.md"
fi

# Generate OpenCode AGENTS.md from base-instructions.md
echo -e "${YELLOW}Generating:${NC} OpenCode AGENTS.md"
if [ -f "$SHARED_DIR/base-instructions.md" ]; then
    cp "$SHARED_DIR/base-instructions.md" "$BUILD_DIR/opencode/AGENTS.md"
    echo "  Created: opencode/AGENTS.md"
fi

echo ""
echo -e "${GREEN}Build complete!${NC}"
echo ""
echo "Generated files:"
echo "  Claude:"
find "$BUILD_DIR/claude" -type f -name "*.md" | sed 's|'"$BUILD_DIR/"'|    |'
echo ""
echo "  OpenCode:"
find "$BUILD_DIR/opencode" -type f -name "*.md" | sed 's|'"$BUILD_DIR/"'|    |'
echo ""
echo "Run ./install.sh to install these configs."
