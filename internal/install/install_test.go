package install

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestRunKeepsExistingFilesWhenOverwriteDeclined(t *testing.T) {
	repoRoot := t.TempDir()
	buildDir := filepath.Join(repoRoot, "build")
	homeDir := filepath.Join(repoRoot, "home")

	writeTestFile(t, filepath.Join(buildDir, "claude", "agents", "review.md"), "original-agent\n")
	writeTestFile(t, filepath.Join(buildDir, "claude", "CLAUDE.md"), "original-base\n")

	if err := Run(Options{
		RepoRoot:      repoRoot,
		BuildDir:      buildDir,
		HomeDir:       homeDir,
		InstallClaude: true,
		SkipBuild:     true,
		Force:         true,
		Stdin:         strings.NewReader(""),
		Stdout:        &bytes.Buffer{},
	}); err != nil {
		t.Fatalf("seed install failed: %v", err)
	}

	writeTestFile(t, filepath.Join(buildDir, "claude", "agents", "review.md"), "updated-agent\n")
	writeTestFile(t, filepath.Join(buildDir, "claude", "CLAUDE.md"), "updated-base\n")

	var output bytes.Buffer
	if err := Run(Options{
		RepoRoot:      repoRoot,
		BuildDir:      buildDir,
		HomeDir:       homeDir,
		InstallClaude: true,
		SkipBuild:     true,
		Stdin:         strings.NewReader("n\nn\n"),
		Stdout:        &output,
	}); err != nil {
		t.Fatalf("install with declined overwrite failed: %v", err)
	}

	assertFileContent(t, filepath.Join(homeDir, ".claude", "agents", "review.md"), "original-agent\n")
	assertFileContent(t, filepath.Join(homeDir, ".claude", "CLAUDE.md"), "original-base\n")
	if !strings.Contains(output.String(), "Skipped agents/review.md") {
		t.Fatalf("expected skip message, got %q", output.String())
	}
}

func TestRunOverwritesExistingSkillDirectoryWhenConfirmed(t *testing.T) {
	repoRoot := t.TempDir()
	buildDir := filepath.Join(repoRoot, "build")
	homeDir := filepath.Join(repoRoot, "home")

	writeTestFile(t, filepath.Join(buildDir, "opencode", "skill", "brainstorming", "SKILL.md"), "original-skill\n")
	writeTestFile(t, filepath.Join(buildDir, "opencode", "AGENTS.md"), "original-agents\n")

	if err := Run(Options{
		RepoRoot:        repoRoot,
		BuildDir:        buildDir,
		HomeDir:         homeDir,
		InstallOpenCode: true,
		SkipBuild:       true,
		Force:           true,
		Stdin:           strings.NewReader(""),
		Stdout:          &bytes.Buffer{},
	}); err != nil {
		t.Fatalf("seed install failed: %v", err)
	}

	writeTestFile(t, filepath.Join(buildDir, "opencode", "skill", "brainstorming", "SKILL.md"), "updated-skill\n")
	writeTestFile(t, filepath.Join(buildDir, "opencode", "AGENTS.md"), "updated-agents\n")

	if err := Run(Options{
		RepoRoot:        repoRoot,
		BuildDir:        buildDir,
		HomeDir:         homeDir,
		InstallOpenCode: true,
		SkipBuild:       true,
		Stdin:           strings.NewReader("y\ny\n"),
		Stdout:          &bytes.Buffer{},
	}); err != nil {
		t.Fatalf("install with confirmed overwrite failed: %v", err)
	}

	assertFileContent(t, filepath.Join(homeDir, ".config", "opencode", "skill", "brainstorming", "SKILL.md"), "updated-skill\n")
	assertFileContent(t, filepath.Join(homeDir, ".config", "opencode", "AGENTS.md"), "updated-agents\n")
}

func TestInitOpenCodeKeepsExistingConfigWhenOverwriteDeclined(t *testing.T) {
	repoRoot := t.TempDir()
	homeDir := filepath.Join(repoRoot, "home")
	writeTestFile(t, filepath.Join(repoRoot, "source", "opencode.json"), "{\n  \"version\": 1\n}\n")

	if err := InitOpenCode(InitOptions{
		RepoRoot: repoRoot,
		HomeDir:  homeDir,
		Force:    true,
		Stdin:    strings.NewReader(""),
		Stdout:   &bytes.Buffer{},
	}); err != nil {
		t.Fatalf("seed init failed: %v", err)
	}

	writeTestFile(t, filepath.Join(repoRoot, "source", "opencode.json"), "{\n  \"version\": 2\n}\n")

	var output bytes.Buffer
	if err := InitOpenCode(InitOptions{
		RepoRoot: repoRoot,
		HomeDir:  homeDir,
		Stdin:    strings.NewReader("n\n"),
		Stdout:   &output,
	}); err != nil {
		t.Fatalf("init with declined overwrite failed: %v", err)
	}

	assertFileContent(t, filepath.Join(homeDir, ".config", "opencode", "opencode.json"), "{\n  \"version\": 1\n}\n")
	if !strings.Contains(output.String(), "OpenCode config unchanged") {
		t.Fatalf("expected unchanged message, got %q", output.String())
	}
}

func TestInitOpenCodeOverwritesExistingConfigWhenConfirmed(t *testing.T) {
	repoRoot := t.TempDir()
	homeDir := filepath.Join(repoRoot, "home")
	writeTestFile(t, filepath.Join(repoRoot, "source", "opencode.json"), "{\n  \"version\": 1\n}\n")

	if err := InitOpenCode(InitOptions{
		RepoRoot: repoRoot,
		HomeDir:  homeDir,
		Force:    true,
		Stdin:    strings.NewReader(""),
		Stdout:   &bytes.Buffer{},
	}); err != nil {
		t.Fatalf("seed init failed: %v", err)
	}

	writeTestFile(t, filepath.Join(repoRoot, "source", "opencode.json"), "{\n  \"version\": 2\n}\n")

	if err := InitOpenCode(InitOptions{
		RepoRoot: repoRoot,
		HomeDir:  homeDir,
		Stdin:    strings.NewReader("y\n"),
		Stdout:   &bytes.Buffer{},
	}); err != nil {
		t.Fatalf("init with confirmed overwrite failed: %v", err)
	}

	assertFileContent(t, filepath.Join(homeDir, ".config", "opencode", "opencode.json"), "{\n  \"version\": 2\n}\n")
}

func writeTestFile(t *testing.T, path, content string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatalf("mkdir %s: %v", filepath.Dir(path), err)
	}
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatalf("write %s: %v", path, err)
	}
}

func assertFileContent(t *testing.T, path, want string) {
	t.Helper()
	got, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read %s: %v", path, err)
	}
	if string(got) != want {
		t.Fatalf("unexpected content for %s\nwant: %q\ngot:  %q", path, want, string(got))
	}
}
