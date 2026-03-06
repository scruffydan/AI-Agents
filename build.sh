#!/usr/bin/env bash

# Build script for AI-Agents
# Generates Claude Code and OpenCode configs from source prompts

set -eu

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_DIR="$REPO_ROOT/source/prompts"
SKILLS_DIR="$REPO_ROOT/source/skills"
BUILD_DIR="$REPO_ROOT/build"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

WORK_MODE_ENABLED=false
UNMAPPED_MODELS=""

# Model mappings file
MODEL_MAPPINGS_FILE="$REPO_ROOT/source/model-mappings.json"

# Transform model based on work mode and mappings
# Output format: "transformed_model<TAB>unmapped_status" (unmapped_status is "1" if not mapped, "0" if mapped)
transform_model() {
    local model="$1"
    [ -z "$model" ] && return
    
    local transformed="$model"
    local unmapped="0"
    local mapped=""
    
    # Check if model is in mappings file (always track unmapped, but only transform in work mode)
    if [ -f "$MODEL_MAPPINGS_FILE" ]; then
        mapped=$(jq -r --arg m "$model" '.models[$m] // empty' "$MODEL_MAPPINGS_FILE" 2>/dev/null)
        
        if [ -n "$mapped" ]; then
            # Only apply transformation in work mode
            if [ "$WORK_MODE_ENABLED" = true ]; then
                transformed="$mapped"
            fi
        else
            unmapped="1"
        fi
    fi
    
    echo -e "$transformed\t$unmapped"
}

# =============================================================================
# Command-line Arguments
# =============================================================================

show_help() {
    echo "Usage: ./build.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --work             Use work environment model mappings"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "By default, OpenCode agents use the opencode provider (e.g. opencode/claude-sonnet-4-6)."
    echo "With --work, models are remapped via source/model-mappings.json:"
    echo "  opencode/claude-sonnet-4-6  ->  google-vertex-anthropic/claude-sonnet-4-5@20250929"
    echo ""
}

while [ $# -gt 0 ]; do
    case $1 in
        --work)
            WORK_MODE_ENABLED=true
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

# Check for jq dependency (needed for model mapping lookups)
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed.${NC}"
    echo "Install with: brew install jq"
    exit 1
fi

echo -e "${GREEN}Building AI-Agents configs...${NC}"
echo "Source: $SHARED_DIR"
echo "Output: $BUILD_DIR"
if [ "$WORK_MODE_ENABLED" = true ]; then
    echo "Mode: work (using model mappings from $MODEL_MAPPINGS_FILE)"
else
    echo "Mode: opencode"
fi
echo ""

# Clean and create build directories
[ -z "$BUILD_DIR" ] && { echo "Error: BUILD_DIR is empty"; exit 1; }
rm -rf -- "$BUILD_DIR"
mkdir -p "$BUILD_DIR/claude/agents" "$BUILD_DIR/claude/commands" "$BUILD_DIR/claude/skills"
mkdir -p "$BUILD_DIR/opencode/agent" "$BUILD_DIR/opencode/command" "$BUILD_DIR/opencode/skill"

# =============================================================================
# Helper Functions
# =============================================================================

# Extract YAML frontmatter from a markdown file
get_frontmatter() {
    sed -n '/^---$/,/^---$/p' "$1" | sed '1d;$d'
}

# Extract content after frontmatter (everything after the closing --- of YAML frontmatter)
# State machine: p=0 (before first ---), p=1 (in frontmatter), p=2 (found closing ---), p=3 (printing content)
# When we hit the second ---, we skip it with getline and start printing from the next line
get_content() {
    awk '
      # p tracks frontmatter parsing state:
      # 0 = before first ---
      # 1 = inside frontmatter
      # 2 = found closing ---
      # 3 = printing content after frontmatter
      BEGIN { p = 0 }
      /^---$/ {
        p++
        if (p == 2) { getline; p = 3 }
        next
      }
      p == 3 { print }
    ' "$1"
}

# Process {{include:filename}} directives in content
# Replaces each directive with the contents of the referenced file from SHARED_DIR
process_includes() {
    local content="$1"
    local include_pattern='\{\{include:([^}]+)\}\}'
    
    while echo "$content" | grep -qE "$include_pattern"; do
        local include_file
        include_file=$(echo "$content" | grep -oE "$include_pattern" | head -1 | sed 's/{{include://;s/}}//')
        local include_path="$SHARED_DIR/$include_file"
        
        if [ -f "$include_path" ]; then
            local include_content
            include_content=$(cat "$include_path")
            local placeholder="{{include:$include_file}}"
            # Split content at the placeholder and reassemble with include content
            local before="${content%%"$placeholder"*}"
            local after="${content#*"$placeholder"}"
            content="${before}${include_content}${after}"
        else
            echo -e "${RED}Warning: Include file not found: $include_path${NC}" >&2
            break
        fi
    done
    
    echo "$content"
}

# Get a value from frontmatter using yq
# Usage: yaml_get "$frontmatter" ".key" or ".parent.child"
yaml_get() {
    local result
    result=$(echo "$1" | yq "$2" 2>/dev/null)
    if [ "$result" = "null" ] || [ -z "$result" ]; then
        echo ""
    else
        echo "$result"
    fi
}

# Format a YAML object as indented key: value lines
# Input: JSON/YAML object string
# Output: Formatted lines with 2-space indent, empty if input is null/empty
format_yaml_object() {
    local yaml_content="$1"
    [ -z "$yaml_content" ] || [ "$yaml_content" = "null" ] && return
    echo "$yaml_content" | yq -r 'to_entries | .[] | "  " + .key + ": " + .value' 2>/dev/null || true
}

# =============================================================================
# Unified Output Generator
# =============================================================================

# Generate output file with frontmatter and content
# Usage: generate_output <target> <type> <filename>
#   target: claude | opencode
#   type: agent | command
#   filename: output filename (without .md)
# Reads from globals: description, content, is_primary,
#   claude_tools, claude_model, oc_mode, oc_model_transformed,
#   oc_subtask, oc_temperature, oc_permission
generate_output() {
    local target="$1"
    local type="$2"
    local filename="$3"
    
    local output_dir="$BUILD_DIR/$target"
    if [ "$target" = "claude" ]; then
        output_dir+="/${type}s"
    else
        output_dir+="/$type"
    fi
    local output_file="$output_dir/${filename}.md"
    
    {
        echo "---"
        
        if [ "$target" = "claude" ]; then
            # Claude format
            [ "$type" = "agent" ] && echo "name: $filename"
            echo "description: $description"
            [ -n "$claude_tools" ] && echo "tools: $claude_tools"
            [ -n "$claude_model" ] && echo "model: $claude_model"
        else
            # OpenCode format
            echo "description: $description"
            
            if [ "$type" = "agent" ]; then
                if [ "$is_primary" = "true" ]; then
                    echo "mode: primary"
                    [ -n "$oc_temperature" ] && echo "temperature: $oc_temperature"
                else
                    [ -n "$oc_mode" ] && echo "mode: $oc_mode"
                fi
                [ -n "$oc_model_transformed" ] && echo "model: $oc_model_transformed"
                [ -n "$oc_reasoning_effort" ] && echo "reasoningEffort: $oc_reasoning_effort"
                [ -n "$oc_permission" ] && { echo "permission:"; echo "$oc_permission"; }
            else
                # command type
                [ -n "$oc_subtask" ] && echo "subtask: $oc_subtask"
                [ -n "$oc_model_transformed" ] && echo "model: $oc_model_transformed"
            fi
        fi
        
        echo "---"
        echo ""
        echo "$content"
    } > "$output_file"
    
    local suffix=""
    [ "$is_primary" = "true" ] && suffix=" (primary)"
    echo "  Created: ${output_file#"$BUILD_DIR"/}$suffix"
}

# =============================================================================
# Main Processing
# =============================================================================

for prompt_file in "$SHARED_DIR"/*.md; do
    filename=$(basename "$prompt_file" .md)
    
    # Skip AGENTS instructions (handled separately) and partial includes (prefixed with _)
    [ "$filename" = "AGENTS" ] && continue
    [ "${filename#_}" != "$filename" ] && continue
    
    echo -e "${YELLOW}Processing:${NC} $filename"
    
    # Parse frontmatter and content
    frontmatter=$(get_frontmatter "$prompt_file")
    content=$(get_content "$prompt_file")
    content=$(process_includes "$content")
    
    # Extract common values
    description=$(yaml_get "$frontmatter" ".description")
    # Valid type values: subagent, command, mode
    type=$(yaml_get "$frontmatter" ".type")
    
    # Extract Claude-specific values
    claude_tools=$(yaml_get "$frontmatter" ".claude.tools")
    claude_model=$(yaml_get "$frontmatter" ".claude.model")
    
    # Extract OpenCode-specific values
    oc_mode=$(yaml_get "$frontmatter" ".opencode.mode")
    oc_model=$(yaml_get "$frontmatter" ".opencode.model")
    oc_subtask=$(yaml_get "$frontmatter" ".opencode.subtask")
    oc_temperature=$(yaml_get "$frontmatter" ".opencode.temperature")
    oc_reasoning_effort=$(yaml_get "$frontmatter" ".opencode.reasoningEffort")
    oc_permission=$(format_yaml_object "$(yaml_get "$frontmatter" ".opencode.permission")")
    
    # Transform model and track unmapped models
    IFS=$'\t' read -r oc_model_transformed is_unmapped <<< "$(transform_model "$oc_model")"
    if [ "$is_unmapped" = "1" ] && [ -n "$oc_model" ]; then
        if [ -z "$UNMAPPED_MODELS" ]; then
            UNMAPPED_MODELS="$oc_model"
        else
            UNMAPPED_MODELS="$UNMAPPED_MODELS
$oc_model"
        fi
    fi
    
    # Determine what to generate based on type
    case "$type" in
        subagent)
            is_primary="false"
            generate_output "claude" "agent" "$filename"
            generate_output "opencode" "agent" "$filename"
            ;;
        command)
            is_primary="false"
            generate_output "claude" "command" "$filename"
            generate_output "opencode" "command" "$filename"
            ;;
        mode)
            is_primary="true"
            generate_output "opencode" "agent" "$filename"
            ;;
        *)
            echo "Unknown type: $type (file: $prompt_file)"
            exit 1
            ;;
    esac
    
    echo ""
done

# Generate base instruction files
echo -e "${YELLOW}Generating:${NC} Base instruction files"
if [ -f "$SHARED_DIR/AGENTS.md" ]; then
    cp "$SHARED_DIR/AGENTS.md" "$BUILD_DIR/claude/CLAUDE.md"
    echo "  Created: claude/CLAUDE.md (Claude Code base instructions)"
    echo ""
    cp "$SHARED_DIR/AGENTS.md" "$BUILD_DIR/opencode/AGENTS.md"
    echo "  Created: opencode/AGENTS.md (OpenCode base instructions)"
fi

# Copy skills to both platforms
echo ""
echo -e "${YELLOW}Copying skills to both platforms...${NC}"
if [ -d "$SKILLS_DIR" ]; then
    skill_count=0
    for skill_dir in "$SKILLS_DIR"/*/; do
        [ -d "$skill_dir" ] || continue
        skill_name=$(basename "$skill_dir")
        
        if [ -f "$skill_dir/SKILL.md" ]; then
            # Create skill directory and copy contents
            mkdir -p "$BUILD_DIR/claude/skills/$skill_name"
            mkdir -p "$BUILD_DIR/opencode/skill/$skill_name"
            cp -r "$skill_dir"* "$BUILD_DIR/claude/skills/$skill_name/"
            cp -r "$skill_dir"* "$BUILD_DIR/opencode/skill/$skill_name/"
            echo "  Created: claude/skills/$skill_name/ and opencode/skill/$skill_name/"
            ((skill_count++))
        fi
    done
    echo ""
    echo "  Total skills copied: $skill_count (to both Claude and OpenCode)"
else
    echo "  No skills directory found, skipping..."
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Build complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Generated files:"
echo ""
echo "  Claude Code ($(find "$BUILD_DIR/claude" -type f -name "*.md" | wc -l | tr -d ' ') files):"
find "$BUILD_DIR/claude" -type f -name "*.md" | sed "s|$BUILD_DIR/|    |" | sort
echo ""
echo "  OpenCode ($(find "$BUILD_DIR/opencode" -type f -name "*.md" | wc -l | tr -d ' ') files):"
find "$BUILD_DIR/opencode" -type f -name "*.md" | sed "s|$BUILD_DIR/|    |" | sort
echo ""

# Write unmapped models to file for install.sh to read
if [ -n "$UNMAPPED_MODELS" ]; then
    echo "$UNMAPPED_MODELS" | sort -u > "$BUILD_DIR/.unmapped-models"
    echo -e "${YELLOW}⚠ Warning: The following models were not mapped in $MODEL_MAPPINGS_FILE:${NC}"
    sed 's/^/  - /' "$BUILD_DIR/.unmapped-models"
    echo ""
    echo "These models will use their original opencode/ provider."
    echo "Add mappings to $MODEL_MAPPINGS_FILE if needed."
    echo ""
else
    rm -f -- "$BUILD_DIR/.unmapped-models"
fi

echo "Next step: Run ./install.sh to install these configs"
echo "  - Install both:        ./install.sh"
echo "  - Install Claude only: ./install.sh --claude"
echo "  - Install OpenCode:    ./install.sh --opencode"
