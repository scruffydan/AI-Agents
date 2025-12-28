#!/usr/bin/env bash

# Build script for AI-Agents
# Generates Claude Code and OpenCode configs from source prompts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_DIR="$SCRIPT_DIR/source/prompts"
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
mkdir -p "$BUILD_DIR/opencode/mode"
mkdir -p "$BUILD_DIR/opencode/rules"

# Function to extract YAML value from frontmatter
# Usage: get_yaml_value "$frontmatter" "key"
# Matches lines like "key: value" and extracts the value
get_yaml_value() {
    local content="$1"
    local key="$2"
    echo "$content" | grep -E "^${key}:" | head -1 | sed "s/^${key}:[[:space:]]*//"
}

# Function to extract nested YAML value
# Usage: get_nested_yaml "$frontmatter" "parent" "child"
# Matches YAML like:
#   parent:
#     child: value
# Returns the value after "child:"
get_nested_yaml() {
    local content="$1"
    local parent="$2"
    local child="$3"
    # Awk logic:
    # 1. Find line starting with "parent:" -> enter parent block
    # 2. Exit parent block when hitting another top-level key (no indent)
    # 3. Within parent block, find "  child:" and extract value after it
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
# Looks within the "claude:" block for a "tools:" line
get_claude_tools() {
    local content="$1"
    # Awk logic:
    # 1. Enter claude block when seeing "claude:"
    # 2. Exit when hitting another top-level key
    # 3. Find "  tools:" line and return everything after it
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
# Same pattern as get_claude_tools but for "model:" line
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

# Function to extract the entire OpenCode config block
# Returns all lines under "opencode:" until the next top-level key
get_opencode_block() {
    local content="$1"
    echo "$content" | awk '
        /^opencode:/ { in_oc=1; next }
        in_oc && /^[a-z]/ { exit }
        in_oc { print }
    '
}

# Function to extract OpenCode temperature
get_opencode_temperature() {
    local content="$1"
    echo "$content" | awk '
        /^opencode:/ { in_oc=1; next }
        in_oc && /^[a-z]/ { in_oc=0 }
        in_oc && /^  temperature:/ { 
            sub(/^  temperature:[[:space:]]*/, ""); 
            print; 
            exit 
        }
    '
}

# Function to check if type includes "agent"
has_agent() {
    local type="$1"
    [[ "$type" == *"agent"* ]]
}

# Function to check if type includes "command"
has_command() {
    local type="$1"
    [[ "$type" == *"command"* ]]
}

# Function to check if type includes "mode"
has_mode() {
    local type="$1"
    [[ "$type" == "mode-only" ]]
}

# =============================================================================
# Parsing Functions
# =============================================================================

# Parse a prompt file and extract frontmatter and content into global variables
# Sets: file_content, frontmatter, content
parse_prompt_file() {
    local file="$1"
    file_content=$(cat "$file")
    
    # Extract frontmatter (between first two ---)
    frontmatter=$(echo "$file_content" | awk '/^---$/{p=!p; if(p) next; else exit} p')
    
    # Extract content (everything after the second ---)
    content=$(echo "$file_content" | awk 'BEGIN{p=0} /^---$/{p++; if(p==2) {getline; p=3}} p==3{print}')
}

# Parse OpenCode-specific values from frontmatter
# Sets: opencode_block, opencode_mode, opencode_model, opencode_subtask, opencode_temperature, opencode_tools
parse_opencode_values() {
    opencode_block=$(get_opencode_block "$frontmatter")
    opencode_mode=$(echo "$opencode_block" | grep -E "^  mode:" | sed 's/^  mode:[[:space:]]*//')
    opencode_model=$(echo "$opencode_block" | grep -E "^  model:" | sed 's/^  model:[[:space:]]*//')
    opencode_subtask=$(echo "$opencode_block" | grep -E "^  subtask:" | sed 's/^  subtask:[[:space:]]*//')
    opencode_temperature=$(get_opencode_temperature "$frontmatter")
    
    # Extract OpenCode tools block
    opencode_tools=$(echo "$opencode_block" | awk '
        /^  tools:/ { in_tools=1; next }
        in_tools && /^  [a-z]/ && !/^    / { exit }
        in_tools { print }
    ')
}

# =============================================================================
# Claude Generation Functions
# =============================================================================

# Generate Claude agent file
generate_claude_agent() {
    local filename="$1"
    local output_file="$BUILD_DIR/claude/agents/$filename.md"
    {
        echo "---"
        echo "name: $filename"
        echo "description: $description"
        [ -n "$claude_tools" ] && echo "tools: $claude_tools"
        [ -n "$claude_model" ] && echo "model: $claude_model"
        echo "---"
        echo ""
        echo "$content"
    } > "$output_file"
    echo "  Created: claude/agents/$filename.md"
}

# Generate Claude command file
generate_claude_command() {
    local filename="$1"
    local output_file="$BUILD_DIR/claude/commands/$filename.md"
    echo "$content" > "$output_file"
    echo "  Created: claude/commands/$filename.md"
}

# =============================================================================
# OpenCode Generation Functions
# =============================================================================

# Generate OpenCode agent file
generate_opencode_agent() {
    local filename="$1"
    local output_file="$BUILD_DIR/opencode/agent/$filename.md"
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
    } > "$output_file"
    echo "  Created: opencode/agent/$filename.md"
}

# Generate OpenCode command file (for command-only types)
generate_opencode_command() {
    local filename="$1"
    local output_file="$BUILD_DIR/opencode/command/$filename.md"
    {
        echo "---"
        echo "description: $description"
        [ -n "$opencode_subtask" ] && echo "subtask: $opencode_subtask"
        [ -n "$opencode_model" ] && echo "model: $opencode_model"
        echo "---"
        echo ""
        echo "$content"
    } > "$output_file"
    echo "  Created: opencode/command/$filename.md"
}

# Generate OpenCode mode file
generate_opencode_mode() {
    local filename="$1"
    local output_file="$BUILD_DIR/opencode/mode/$filename.md"
    {
        echo "---"
        [ -n "$opencode_model" ] && echo "model: $opencode_model"
        [ -n "$opencode_temperature" ] && echo "temperature: $opencode_temperature"
        if [ -n "$opencode_tools" ]; then
            echo "tools:"
            echo "$opencode_tools"
        fi
        echo "---"
        echo ""
        echo "$content"
    } > "$output_file"
    echo "  Created: opencode/mode/$filename.md"
}

# =============================================================================
# Main Processing
# =============================================================================

# Process each prompt file
for prompt_file in "$SHARED_DIR"/*.md; do
    filename=$(basename "$prompt_file" .md)
    
    # Skip base-instructions (handled separately)
    [ "$filename" = "base-instructions" ] && continue
    
    echo -e "${YELLOW}Processing:${NC} $filename"
    
    # Parse the file
    parse_prompt_file "$prompt_file"
    
    # Get common values
    description=$(get_yaml_value "$frontmatter" "description")
    type=$(get_yaml_value "$frontmatter" "type")
    
    # Get Claude-specific values
    claude_tools=$(get_claude_tools "$frontmatter")
    claude_model=$(get_claude_model "$frontmatter")
    
    # Get OpenCode-specific values
    parse_opencode_values
    
    # Generate Claude files
    has_agent "$type" && generate_claude_agent "$filename"
    has_command "$type" && generate_claude_command "$filename"
    
    # Generate OpenCode files
    has_agent "$type" && generate_opencode_agent "$filename"
    has_command "$type" && ! has_agent "$type" && generate_opencode_command "$filename"
    has_mode "$type" && generate_opencode_mode "$filename"
    
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
