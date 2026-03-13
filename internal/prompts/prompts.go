package prompts

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"

	"go.yaml.in/yaml/v3"
)

type PromptType string

const (
	PromptTypeSubagent PromptType = "subagent"
	PromptTypeCommand  PromptType = "command"
	PromptTypeMode     PromptType = "mode"
)

type PromptDoc struct {
	Name        string
	Description string
	Type        PromptType
	Body        string
	Claude      map[string]any
	OpenCode    map[string]any
	SourcePath  string
}

type ModelMappings struct {
	Models map[string]string `json:"models"`
}

var includePattern = regexp.MustCompile(`\{\{include:([^}]+)\}\}`)

func LoadAll(dir string) ([]PromptDoc, error) {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return nil, fmt.Errorf("read prompts directory %s: %w", dir, err)
	}

	var files []string
	for _, entry := range entries {
		name := entry.Name()
		if entry.IsDir() || filepath.Ext(name) != ".md" {
			continue
		}
		if name == "AGENTS.md" || strings.HasPrefix(name, "_") {
			continue
		}
		files = append(files, filepath.Join(dir, name))
	}
	sort.Strings(files)

	docs := make([]PromptDoc, 0, len(files))
	for _, file := range files {
		doc, err := LoadFile(file, dir)
		if err != nil {
			return nil, err
		}
		docs = append(docs, doc)
	}
	return docs, nil
}

func LoadFile(path, includeDir string) (PromptDoc, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return PromptDoc{}, fmt.Errorf("read prompt %s: %w", path, err)
	}

	frontmatter, body, err := splitFrontmatter(string(raw))
	if err != nil {
		return PromptDoc{}, fmt.Errorf("parse frontmatter %s: %w", path, err)
	}

	var parsed struct {
		Description string         `yaml:"description"`
		Type        PromptType     `yaml:"type"`
		Claude      map[string]any `yaml:"claude"`
		OpenCode    map[string]any `yaml:"opencode"`
	}
	if err := yaml.Unmarshal([]byte(frontmatter), &parsed); err != nil {
		return PromptDoc{}, fmt.Errorf("unmarshal frontmatter %s: %w", path, err)
	}

	expandedBody, err := expandIncludes(body, includeDir, nil)
	if err != nil {
		return PromptDoc{}, fmt.Errorf("expand includes %s: %w", path, err)
	}

	return PromptDoc{
		Name:        strings.TrimSuffix(filepath.Base(path), filepath.Ext(path)),
		Description: parsed.Description,
		Type:        parsed.Type,
		Body:        expandedBody,
		Claude:      cloneMap(parsed.Claude),
		OpenCode:    cloneMap(parsed.OpenCode),
		SourcePath:  path,
	}, nil
}

func LoadModelMappings(path string) (ModelMappings, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return ModelMappings{}, fmt.Errorf("read model mappings %s: %w", path, err)
	}

	var mappings ModelMappings
	if err := json.Unmarshal(raw, &mappings); err != nil {
		return ModelMappings{}, fmt.Errorf("parse model mappings %s: %w", path, err)
	}
	if mappings.Models == nil {
		mappings.Models = map[string]string{}
	}
	return mappings, nil
}

func GetString(values map[string]any, key string) string {
	if values == nil {
		return ""
	}
	value, ok := values[key]
	if !ok || value == nil {
		return ""
	}
	return fmt.Sprint(value)
}

func CloneMap(values map[string]any) map[string]any {
	return cloneMap(values)
}

func splitFrontmatter(raw string) (string, string, error) {
	normalized := strings.ReplaceAll(raw, "\r\n", "\n")
	if !strings.HasPrefix(normalized, "---\n") {
		return "", "", fmt.Errorf("missing opening frontmatter delimiter")
	}

	remainder := strings.TrimPrefix(normalized, "---\n")
	idx := strings.Index(remainder, "\n---\n")
	if idx < 0 {
		return "", "", fmt.Errorf("missing closing frontmatter delimiter")
	}

	frontmatter := remainder[:idx]
	body := remainder[idx+len("\n---\n"):]
	return frontmatter, body, nil
}

func expandIncludes(body, dir string, stack []string) (string, error) {
	matches := includePattern.FindAllStringSubmatchIndex(body, -1)
	if len(matches) == 0 {
		return body, nil
	}

	var builder strings.Builder
	last := 0
	for _, match := range matches {
		start, end := match[0], match[1]
		fileStart, fileEnd := match[2], match[3]
		includeFile := body[fileStart:fileEnd]

		builder.WriteString(body[last:start])

		if contains(stack, includeFile) {
			return "", fmt.Errorf("include cycle detected: %s", strings.Join(append(stack, includeFile), " -> "))
		}

		includePath := filepath.Join(dir, includeFile)
		content, err := os.ReadFile(includePath)
		if err != nil {
			return "", fmt.Errorf("read include %s: %w", includePath, err)
		}

		expanded, err := expandIncludes(string(content), dir, append(stack, includeFile))
		if err != nil {
			return "", err
		}
		builder.WriteString(expanded)
		last = end
	}

	builder.WriteString(body[last:])
	return builder.String(), nil
}

func contains(values []string, target string) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}
	return false
}

func cloneMap(values map[string]any) map[string]any {
	if len(values) == 0 {
		return map[string]any{}
	}
	cloned := make(map[string]any, len(values))
	for key, value := range values {
		cloned[key] = cloneValue(value)
	}
	return cloned
}

func cloneValue(value any) any {
	switch typed := value.(type) {
	case map[string]any:
		return cloneMap(typed)
	case []any:
		cloned := make([]any, 0, len(typed))
		for _, item := range typed {
			cloned = append(cloned, cloneValue(item))
		}
		return cloned
	default:
		return typed
	}
}
