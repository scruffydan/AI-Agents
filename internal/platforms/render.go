package platforms

import (
	"bytes"
	"fmt"
	"sort"
	"strings"

	"ai-agents/internal/prompts"
	"go.yaml.in/yaml/v3"
)

type Artifact struct {
	Path    string
	Content []byte
}

type frontmatterField struct {
	key   string
	value any
}

func ClaudeArtifact(doc prompts.PromptDoc) (*Artifact, error) {
	if doc.Type == prompts.PromptTypeMode {
		return nil, nil
	}

	fields := []frontmatterField{
		{key: "description", value: doc.Description},
	}
	if doc.Type == prompts.PromptTypeSubagent {
		fields = append(fields, frontmatterField{key: "name", value: doc.Name})
	}
	fields = append(fields,
		frontmatterField{key: "tools", value: prompts.GetString(doc.Claude, "tools")},
		frontmatterField{key: "model", value: prompts.GetString(doc.Claude, "model")},
	)

	content, err := marshalDocument(fields, nil, doc.Body)
	if err != nil {
		return nil, err
	}

	dir := "claude/commands"
	if doc.Type == prompts.PromptTypeSubagent {
		dir = "claude/agents"
	}

	return &Artifact{Path: dir + "/" + doc.Name + ".md", Content: content}, nil
}

func OpenCodeArtifact(doc prompts.PromptDoc, transformedModel string) (*Artifact, error) {
	frontmatter := prompts.CloneMap(doc.OpenCode)
	if frontmatter == nil {
		frontmatter = map[string]any{}
	}

	fields := []frontmatterField{{key: "description", value: doc.Description}}

	switch doc.Type {
	case prompts.PromptTypeMode:
		delete(frontmatter, "mode")
		fields = append(fields, frontmatterField{key: "mode", value: "primary"})
	case prompts.PromptTypeSubagent:
		mode := prompts.GetString(frontmatter, "mode")
		delete(frontmatter, "mode")
		fields = append(fields, frontmatterField{key: "mode", value: mode})
	case prompts.PromptTypeCommand:
		delete(frontmatter, "mode")
	}

	delete(frontmatter, "model")
	fields = append(fields, frontmatterField{key: "model", value: transformedModel})

	if permission, ok := frontmatter["permission"]; ok && doc.Type != prompts.PromptTypeCommand {
		delete(frontmatter, "permission")
		fields = append(fields, frontmatterField{key: "permission", value: permission})
	}

	content, err := marshalDocument(fields, frontmatter, doc.Body)
	if err != nil {
		return nil, err
	}

	dir := "opencode/command"
	if doc.Type != prompts.PromptTypeCommand {
		dir = "opencode/agent"
	}

	return &Artifact{Path: dir + "/" + doc.Name + ".md", Content: content}, nil
}

func marshalDocument(fields []frontmatterField, extra map[string]any, body string) ([]byte, error) {
	var buf bytes.Buffer
	buf.WriteString("---\n")
	for _, field := range fields {
		if isEmpty(field.value) {
			continue
		}
		if err := writeField(&buf, field.key, field.value, 0); err != nil {
			return nil, err
		}
	}
	for _, key := range sortedKeys(extra) {
		value := extra[key]
		if isEmpty(value) {
			continue
		}
		if err := writeField(&buf, key, value, 0); err != nil {
			return nil, err
		}
	}
	buf.WriteString("---\n\n")
	buf.WriteString(strings.TrimLeft(body, "\n"))
	if !strings.HasSuffix(body, "\n") {
		buf.WriteString("\n")
	}
	return buf.Bytes(), nil
}

func writeField(buf *bytes.Buffer, key string, value any, indent int) error {
	prefix := strings.Repeat("  ", indent)
	value = normalize(value)
	if inline, ok, err := inlineScalar(value); err != nil {
		return err
	} else if ok {
		buf.WriteString(prefix)
		buf.WriteString(key)
		buf.WriteString(": ")
		buf.WriteString(inline)
		buf.WriteByte('\n')
		return nil
	}

	buf.WriteString(prefix)
	buf.WriteString(key)
	buf.WriteString(":\n")
	return writeValue(buf, value, indent+1)
}

func writeValue(buf *bytes.Buffer, value any, indent int) error {
	prefix := strings.Repeat("  ", indent)
	switch typed := value.(type) {
	case map[string]any:
		for _, key := range sortedKeys(typed) {
			if isEmpty(typed[key]) {
				continue
			}
			if err := writeField(buf, key, typed[key], indent); err != nil {
				return err
			}
		}
	case []any:
		for _, item := range typed {
			item = normalize(item)
			if inline, ok, err := inlineScalar(item); err != nil {
				return err
			} else if ok {
				buf.WriteString(prefix)
				buf.WriteString("- ")
				buf.WriteString(inline)
				buf.WriteByte('\n')
				continue
			}
			buf.WriteString(prefix)
			buf.WriteString("-\n")
			if err := writeValue(buf, item, indent+1); err != nil {
				return err
			}
		}
	default:
		inline, _, err := inlineScalar(typed)
		if err != nil {
			return err
		}
		buf.WriteString(prefix)
		buf.WriteString(inline)
		buf.WriteByte('\n')
	}
	return nil
}

func inlineScalar(value any) (string, bool, error) {
	switch typed := value.(type) {
	case nil:
		return "", true, nil
	case map[string]any:
		if len(typed) == 0 {
			return "{}", true, nil
		}
		return "", false, nil
	case []any:
		if len(typed) == 0 {
			return "[]", true, nil
		}
		return "", false, nil
	case string, bool, int, int64, float64:
		raw, err := yaml.Marshal(typed)
		if err != nil {
			return "", false, fmt.Errorf("marshal YAML scalar: %w", err)
		}
		return strings.TrimSpace(string(raw)), true, nil
	default:
		raw, err := yaml.Marshal(typed)
		if err != nil {
			return "", false, fmt.Errorf("marshal YAML value: %w", err)
		}
		trimmed := strings.TrimSpace(string(raw))
		if strings.Contains(trimmed, "\n") {
			return "", false, nil
		}
		return trimmed, true, nil
	}
}

func normalize(value any) any {
	switch typed := value.(type) {
	case map[string]string:
		normalized := make(map[string]any, len(typed))
		for key, value := range typed {
			normalized[key] = value
		}
		return normalized
	case map[string]any:
		normalized := make(map[string]any, len(typed))
		for key, value := range typed {
			normalized[key] = normalize(value)
		}
		return normalized
	case map[any]any:
		normalized := make(map[string]any, len(typed))
		for key, value := range typed {
			normalized[fmt.Sprint(key)] = normalize(value)
		}
		return normalized
	case []string:
		normalized := make([]any, 0, len(typed))
		for _, value := range typed {
			normalized = append(normalized, value)
		}
		return normalized
	case []any:
		normalized := make([]any, 0, len(typed))
		for _, value := range typed {
			normalized = append(normalized, normalize(value))
		}
		return normalized
	default:
		return typed
	}
}

func isEmpty(value any) bool {
	value = normalize(value)
	switch typed := value.(type) {
	case nil:
		return true
	case string:
		return typed == ""
	case map[string]any:
		return len(typed) == 0
	case []any:
		return len(typed) == 0
	default:
		return false
	}
}

func sortedKeys(values map[string]any) []string {
	if len(values) == 0 {
		return nil
	}
	keys := make([]string, 0, len(values))
	for key := range values {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}
