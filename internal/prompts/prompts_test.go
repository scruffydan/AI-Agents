package prompts

import (
	"path/filepath"
	"strings"
	"testing"

	"os"
)

func TestLoadFileExpandsNestedIncludes(t *testing.T) {
	tempDir := t.TempDir()

	if err := os.WriteFile(filepath.Join(tempDir, "_inner.md"), []byte("INNER"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(tempDir, "_outer.md"), []byte("before {{include:_inner.md}} after"), 0o644); err != nil {
		t.Fatal(err)
	}
	prompt := strings.Join([]string{
		"---",
		"description: test",
		"type: subagent",
		"claude: {}",
		"opencode:",
		"  mode: subagent",
		"---",
		"Hello {{include:_outer.md}} world",
	}, "\n")
	path := filepath.Join(tempDir, "example.md")
	if err := os.WriteFile(path, []byte(prompt), 0o644); err != nil {
		t.Fatal(err)
	}

	doc, err := LoadFile(path, tempDir)
	if err != nil {
		t.Fatalf("LoadFile returned error: %v", err)
	}

	want := "Hello before INNER after world"
	if doc.Body != want {
		t.Fatalf("unexpected body\nwant: %q\ngot:  %q", want, doc.Body)
	}
}

func TestLoadFileDetectsIncludeCycle(t *testing.T) {
	tempDir := t.TempDir()
	if err := os.WriteFile(filepath.Join(tempDir, "_a.md"), []byte("{{include:_b.md}}"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(tempDir, "_b.md"), []byte("{{include:_a.md}}"), 0o644); err != nil {
		t.Fatal(err)
	}
	prompt := strings.Join([]string{
		"---",
		"description: test",
		"type: subagent",
		"claude: {}",
		"opencode:",
		"  mode: subagent",
		"---",
		"{{include:_a.md}}",
	}, "\n")
	path := filepath.Join(tempDir, "example.md")
	if err := os.WriteFile(path, []byte(prompt), 0o644); err != nil {
		t.Fatal(err)
	}

	_, err := LoadFile(path, tempDir)
	if err == nil || !strings.Contains(err.Error(), "include cycle detected") {
		t.Fatalf("expected include cycle error, got %v", err)
	}
}
