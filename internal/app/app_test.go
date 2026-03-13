package app

import (
	"bytes"
	"strings"
	"testing"
)

func TestRootHelpIncludesExamples(t *testing.T) {
	var stdout bytes.Buffer
	var stderr bytes.Buffer

	if err := Run(nil, &stdout, &stderr); err != nil {
		t.Fatalf("Run returned error: %v", err)
	}

	output := stdout.String()
	for _, want := range []string{
		"Usage: ai-agents <command> [options]",
		"Examples:",
		"ai-agents install --all --yes",
	} {
		if !strings.Contains(output, want) {
			t.Fatalf("expected %q in root help, got %q", want, output)
		}
	}
}

func TestBuildHelpIncludesExamples(t *testing.T) {
	var stdout bytes.Buffer
	var stderr bytes.Buffer

	if err := Run([]string{"build", "--help"}, &stdout, &stderr); err != nil {
		t.Fatalf("Run returned error: %v", err)
	}

	output := stdout.String()
	for _, want := range []string{
		"Usage: ai-agents build [options]",
		"Examples:",
		"ai-agents build --chatgpt-provider github-copilot",
	} {
		if !strings.Contains(output, want) {
			t.Fatalf("expected %q in build help, got %q", want, output)
		}
	}
}

func TestInstallHelpIncludesInteractiveNote(t *testing.T) {
	var stdout bytes.Buffer
	var stderr bytes.Buffer

	if err := Run([]string{"install", "--help"}, &stdout, &stderr); err != nil {
		t.Fatalf("Run returned error: %v", err)
	}

	output := stdout.String()
	for _, want := range []string{
		"Usage: ai-agents install [options]",
		"If no target is specified, the command prompts for a destination.",
		"ai-agents install --all --skip-build",
	} {
		if !strings.Contains(output, want) {
			t.Fatalf("expected %q in install help, got %q", want, output)
		}
	}
}
