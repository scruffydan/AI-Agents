package prompts

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"go.yaml.in/yaml/v3"
)

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

	parsed, err := parseFrontmatter(frontmatter)
	if err != nil {
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

type frontmatter struct {
	Description string         `yaml:"description"`
	Type        PromptType     `yaml:"type"`
	Claude      map[string]any `yaml:"claude"`
	OpenCode    map[string]any `yaml:"opencode"`
}

func parseFrontmatter(raw string) (frontmatter, error) {
	var parsed frontmatter
	if err := yaml.Unmarshal([]byte(raw), &parsed); err != nil {
		return frontmatter{}, err
	}
	return parsed, nil
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
