package buildsys

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"ai-agents/internal/files"
	"ai-agents/internal/platforms"
	"ai-agents/internal/prompts"
)

const defaultProvider = "openai"

type Options struct {
	RepoRoot        string
	OutputDir       string
	WorkMode        bool
	ChatGPTProvider string
	Stdout          io.Writer
}

func Run(opts Options) error {
	if opts.RepoRoot == "" {
		return fmt.Errorf("repo root is required")
	}
	if opts.Stdout == nil {
		opts.Stdout = io.Discard
	}
	if opts.ChatGPTProvider == "" {
		opts.ChatGPTProvider = defaultProvider
	}
	if !validProvider(opts.ChatGPTProvider) {
		return fmt.Errorf("invalid ChatGPT provider %q", opts.ChatGPTProvider)
	}

	outputDir := opts.OutputDir
	if outputDir == "" {
		outputDir = filepath.Join(opts.RepoRoot, "build")
	}
	if !filepath.IsAbs(outputDir) {
		outputDir = filepath.Join(opts.RepoRoot, outputDir)
	}

	promptsDir := filepath.Join(opts.RepoRoot, "source", "prompts")
	skillsDir := filepath.Join(opts.RepoRoot, "source", "skills")
	mappingsPath := filepath.Join(opts.RepoRoot, "source", "model-mappings.json")

	docs, err := prompts.LoadAll(promptsDir)
	if err != nil {
		return err
	}
	mappings, err := prompts.LoadModelMappings(mappingsPath)
	if err != nil {
		return err
	}

	if err := files.ResetDir(outputDir); err != nil {
		return err
	}

	unmappedSet := map[string]struct{}{}
	var artifactCount int
	for _, doc := range docs {
		selectedModel := prompts.GetString(doc.OpenCode, "model")
		if !opts.WorkMode {
			selectedModel = selectChatGPTProvider(selectedModel, opts.ChatGPTProvider)
		}
		transformedModel, unmapped := transformModel(selectedModel, mappings, opts.WorkMode)
		if unmapped {
			unmappedSet[selectedModel] = struct{}{}
		}

		claudeArtifact, err := platforms.ClaudeArtifact(doc)
		if err != nil {
			return fmt.Errorf("render Claude artifact for %s: %w", doc.Name, err)
		}
		if claudeArtifact != nil {
			if err := files.WriteFile(filepath.Join(outputDir, claudeArtifact.Path), claudeArtifact.Content); err != nil {
				return err
			}
			artifactCount++
		}

		opencodeArtifact, err := platforms.OpenCodeArtifact(doc, transformedModel)
		if err != nil {
			return fmt.Errorf("render OpenCode artifact for %s: %w", doc.Name, err)
		}
		if opencodeArtifact != nil {
			if err := files.WriteFile(filepath.Join(outputDir, opencodeArtifact.Path), opencodeArtifact.Content); err != nil {
				return err
			}
			artifactCount++
		}
	}

	if err := copyBaseInstructions(promptsDir, outputDir); err != nil {
		return err
	}
	if err := copySkills(skillsDir, outputDir); err != nil {
		return err
	}
	if err := writeUnmappedModels(outputDir, unmappedSet); err != nil {
		return err
	}

	fmt.Fprintf(opts.Stdout, "Built %d prompts into %s\n", len(docs), outputDir)
	fmt.Fprintf(opts.Stdout, "Wrote %d generated artifacts\n", artifactCount)
	if opts.WorkMode {
		fmt.Fprintln(opts.Stdout, "Mode: work mappings enabled")
	} else {
		fmt.Fprintf(opts.Stdout, "ChatGPT provider: %s\n", opts.ChatGPTProvider)
	}
	return nil
}

func selectChatGPTProvider(model, provider string) string {
	if model == "" {
		return ""
	}
	for _, prefix := range []string{"openai/gpt-", "opencode/gpt-", "github-copilot/gpt-"} {
		if len(model) >= len(prefix) && model[:len(prefix)] == prefix {
			parts := strings.SplitN(model, "/", 2)
			if len(parts) != 2 {
				return model
			}
			return provider + "/" + parts[1]
		}
	}
	return model
}

func transformModel(model string, mappings prompts.ModelMappings, workMode bool) (string, bool) {
	if model == "" {
		return "", false
	}
	mapped, ok := mappings.Models[model]
	if !ok {
		return model, true
	}
	if workMode {
		return mapped, false
	}
	return model, false
}

func validProvider(provider string) bool {
	switch provider {
	case "openai", "opencode", "github-copilot":
		return true
	default:
		return false
	}
}

func copyBaseInstructions(promptsDir, outputDir string) error {
	source := filepath.Join(promptsDir, "AGENTS.md")
	if _, err := os.Stat(source); err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return fmt.Errorf("stat base instructions %s: %w", source, err)
	}
	if err := files.CopyFile(source, filepath.Join(outputDir, "claude", "CLAUDE.md")); err != nil {
		return err
	}
	if err := files.CopyFile(source, filepath.Join(outputDir, "opencode", "AGENTS.md")); err != nil {
		return err
	}
	return nil
}

func copySkills(skillsDir, outputDir string) error {
	entries, err := os.ReadDir(skillsDir)
	if err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return fmt.Errorf("read skills directory %s: %w", skillsDir, err)
	}

	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		source := filepath.Join(skillsDir, entry.Name())
		if err := files.CopyDir(source, filepath.Join(outputDir, "claude", "skills", entry.Name())); err != nil {
			return err
		}
		if err := files.CopyDir(source, filepath.Join(outputDir, "opencode", "skill", entry.Name())); err != nil {
			return err
		}
	}
	return nil
}

func writeUnmappedModels(outputDir string, values map[string]struct{}) error {
	path := filepath.Join(outputDir, ".unmapped-models")
	if len(values) == 0 {
		if err := os.Remove(path); err != nil && !os.IsNotExist(err) {
			return fmt.Errorf("remove %s: %w", path, err)
		}
		return nil
	}

	items := make([]string, 0, len(values))
	for value := range values {
		items = append(items, value)
	}
	sort.Strings(items)
	content := []byte(strings.Join(items, "\n") + "\n")
	return files.WriteFile(path, content)
}
