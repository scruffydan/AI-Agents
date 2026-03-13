package buildsys

import (
	"testing"

	"ai-agents/internal/prompts"
)

func TestTransformModel(t *testing.T) {
	mappings := prompts.ModelMappings{Models: map[string]string{
		"openai/gpt-5.4": "google-vertex/gemini-3.1-pro-preview",
	}}

	transformed, unmapped := transformModel("openai/gpt-5.4", mappings, true)
	if unmapped {
		t.Fatal("expected mapped model")
	}
	if transformed != "google-vertex/gemini-3.1-pro-preview" {
		t.Fatalf("unexpected transformed model %q", transformed)
	}

	transformed, unmapped = transformModel("openai/gpt-5.4", mappings, false)
	if unmapped {
		t.Fatal("expected mapped model in standard mode")
	}
	if transformed != "openai/gpt-5.4" {
		t.Fatalf("unexpected standard mode model %q", transformed)
	}

	transformed, unmapped = transformModel("openai/gpt-missing", mappings, true)
	if !unmapped {
		t.Fatal("expected unmapped model")
	}
	if transformed != "openai/gpt-missing" {
		t.Fatalf("unexpected unmapped model %q", transformed)
	}
}

func TestSelectChatGPTProvider(t *testing.T) {
	got := selectChatGPTProvider("opencode/gpt-5.4", "github-copilot")
	if got != "github-copilot/gpt-5.4" {
		t.Fatalf("unexpected provider selection %q", got)
	}

	unchanged := selectChatGPTProvider("opencode/claude-sonnet-4-6", "github-copilot")
	if unchanged != "opencode/claude-sonnet-4-6" {
		t.Fatalf("unexpected non-GPT rewrite %q", unchanged)
	}
}
