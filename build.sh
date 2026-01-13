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

# Default provider for OpenCode models
OPENCODE_PROVIDER="opencode"

# Get Vertex AI version suffix for a model
get_vertex_version() {
    case "$1" in
        *claude-opus-4-5)    echo "@20251101" ;;
        *claude-sonnet-4-5)  echo "@20250929" ;;
        *claude-haiku-4-5)   echo "@20251001" ;;
        *claude-opus-4-1)    echo "@20250805" ;;
        *claude-opus-4)      echo "@20250514" ;;
        *claude-sonnet-4)    echo "@20250514" ;;
        *claude-3-haiku)     echo "@20240307" ;;
        *)                   echo "" ;;
    esac
}

# =============================================================================
# Command-line Arguments
# =============================================================================

show_help() {
    echo "Usage: ./build.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --opencode         Use OpenCode as the model provider (default)"
    echo "  --vertex           Use Google Vertex AI Anthropic as the model provider"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "The provider selection affects OpenCode agent model strings:"
    echo "  --opencode  ->  opencode/claude-sonnet-4-5"
    echo "  --vertex    ->  google-vertex-anthropic/claude-sonnet-4-5@20250929"
    echo ""
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --opencode)
            OPENCODE_PROVIDER="opencode"
            shift
            ;;
        --vertex)
            OPENCODE_PROVIDER="google-vertex-anthropic"
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

# Check for yq dependency
if ! command -v yq &> /dev/null; then
    echo -e "${RED}Error: yq is required but not installed.${NC}"
    echo "Install with: brew install yq"
    exit 1
fi

echo -e "${GREEN}Building AI-Agents configs...${NC}"
echo "Source: $SHARED_DIR"
echo "Output: $BUILD_DIR"
echo "OpenCode Provider: $OPENCODE_PROVIDER"
echo ""

# Clean and create build directories
[[ -z "$BUILD_DIR" ]] && { echo "Error: BUILD_DIR is empty"; exit 1; }
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/claude/agents" "$BUILD_DIR/claude/commands"
mkdir -p "$BUILD_DIR/opencode/agent" "$BUILD_DIR/opencode/command"

# =============================================================================
# Helper Functions
# =============================================================================

# Extract YAML frontmatter from a markdown file
get_frontmatter() {
    sed -n '/^---$/,/^---$/p' "$1" | sed '1d;$d'
}

# Extract content after frontmatter
get_content() {
    awk 'BEGIN{p=0} /^---$/{p++; if(p==2) {getline; p=3}} p==3{print}' "$1"
}

# Get a value from frontmatter using yq
# Usage: yaml_get "$frontmatter" ".key" or ".parent.child"
yaml_get() {
    local result
    result=$(echo "$1" | yq "$2" 2>/dev/null)
    [[ "$result" == "null" || -z "$result" ]] && echo "" || echo "$result"
}

# Transform OpenCode model string based on selected provider
transform_model() {
    local model="$1"
    [[ -z "$model" ]] && return
    
    local transformed="$model"
    
    # Only transform if not using default opencode provider
    if [[ "$OPENCODE_PROVIDER" != "opencode" ]]; then
        # Replace "opencode/" with the selected provider prefix using sed
        transformed=$(echo "$model" | sed "s|^opencode/|${OPENCODE_PROVIDER}/|")
        
        # For Vertex AI, add version suffix
        if [[ "$OPENCODE_PROVIDER" == "google-vertex-anthropic" ]]; then
            local suffix=$(get_vertex_version "$transformed")
            transformed="${transformed}${suffix}"
        fi
    fi
    
    echo "$transformed"
}

# =============================================================================
# Unified Output Generator
# =============================================================================

# Generate output file with frontmatter and content
# Usage: generate_output <target> <type> <filename> <options>
#   target: claude | opencode
#   type: agent | command
#   filename: output filename (without .md)
generate_output() {
    local target="$1"
    local type="$2"
    local filename="$3"
    
    local output_dir="$BUILD_DIR/$target"
    [[ "$target" == "claude" ]] && output_dir+="/${type}s" || output_dir+="/$type"
    local output_file="$output_dir/$filename.md"
    
    {
        echo "---"
        
        if [[ "$target" == "claude" ]]; then
            # Claude format
            [[ "$type" == "agent" ]] && echo "name: $filename"
            echo "description: $description"
            [[ -n "$claude_tools" ]] && echo "tools: $claude_tools"
            [[ -n "$claude_model" ]] && echo "model: $claude_model"
        else
            # OpenCode format
            echo "description: $description"
            
            if [[ "$type" == "agent" ]]; then
                if [[ "$is_primary" == "true" ]]; then
                    echo "mode: primary"
                    [[ -n "$oc_temperature" ]] && echo "temperature: $oc_temperature"
                else
                    [[ -n "$oc_mode" ]] && echo "mode: $oc_mode"
                fi
                [[ -n "$oc_model_transformed" ]] && echo "model: $oc_model_transformed"
                [[ -n "$oc_permission" ]] && { echo "permission:"; echo "$oc_permission"; }
            else
                # command type
                [[ -n "$oc_subtask" ]] && echo "subtask: $oc_subtask"
                [[ -n "$oc_model_transformed" ]] && echo "model: $oc_model_transformed"
            fi
        fi
        
        echo "---"
        echo ""
        echo "$content"
    } > "$output_file"
    
    local suffix=""
    [[ "$is_primary" == "true" ]] && suffix=" (primary)"
    echo "  Created: ${output_file#$BUILD_DIR/}$suffix"
}

# =============================================================================
# Main Processing
# =============================================================================

for prompt_file in "$SHARED_DIR"/*.md; do
    filename=$(basename "$prompt_file" .md)
    
    # Skip base-instructions (handled separately)
    [[ "$filename" == "base-instructions" ]] && continue
    
    echo -e "${YELLOW}Processing:${NC} $filename"
    
    # Parse frontmatter and content
    frontmatter=$(get_frontmatter "$prompt_file")
    content=$(get_content "$prompt_file")
    
    # Extract common values
    description=$(yaml_get "$frontmatter" ".description")
    type=$(yaml_get "$frontmatter" ".type")
    
    # Extract Claude-specific values
    claude_tools=$(yaml_get "$frontmatter" ".claude.tools")
    claude_model=$(yaml_get "$frontmatter" ".claude.model")
    
    # Extract OpenCode-specific values
    oc_mode=$(yaml_get "$frontmatter" ".opencode.mode")
    oc_model=$(yaml_get "$frontmatter" ".opencode.model")
    oc_subtask=$(yaml_get "$frontmatter" ".opencode.subtask")
    oc_temperature=$(yaml_get "$frontmatter" ".opencode.temperature")
    oc_permission=$(yaml_get "$frontmatter" ".opencode.permission" | yq -r 'to_entries | .[] | "  " + .key + ": " + .value' 2>/dev/null || true)
    oc_model_transformed=$(transform_model "$oc_model")
    
    # Determine what to generate based on type
    is_primary="false"
    
    # Claude outputs
    [[ "$type" == *"agent"* ]] && generate_output "claude" "agent" "$filename"
    [[ "$type" == *"command"* ]] && generate_output "claude" "command" "$filename"
    
    # OpenCode outputs
    if [[ "$type" == *"agent"* ]]; then
        generate_output "opencode" "agent" "$filename"
    elif [[ "$type" == *"command"* ]]; then
        generate_output "opencode" "command" "$filename"
    fi
    
    # mode-only types become primary agents in OpenCode
    if [[ "$type" == "mode-only" ]]; then
        is_primary="true"
        generate_output "opencode" "agent" "$filename"
    fi
    
    echo ""
done

# Generate base instruction files
echo -e "${YELLOW}Generating:${NC} CLAUDE.md"
if [[ -f "$SHARED_DIR/base-instructions.md" ]]; then
    cp "$SHARED_DIR/base-instructions.md" "$BUILD_DIR/claude/CLAUDE.md"
    echo "  Created: claude/CLAUDE.md"
fi

echo -e "${YELLOW}Generating:${NC} OpenCode AGENTS.md"
if [[ -f "$SHARED_DIR/base-instructions.md" ]]; then
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
