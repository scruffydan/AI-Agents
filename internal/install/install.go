package install

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"ai-agents/internal/buildsys"
	"ai-agents/internal/files"
)

const defaultProvider = "openai"

type Options struct {
	RepoRoot        string
	BuildDir        string
	HomeDir         string
	InstallClaude   bool
	InstallOpenCode bool
	SkipBuild       bool
	WorkMode        bool
	Force           bool
	ChatGPTProvider string
	Stdin           io.Reader
	Stdout          io.Writer
}

func Run(opts Options) error {
	if opts.RepoRoot == "" {
		return fmt.Errorf("repo root is required")
	}
	if opts.HomeDir == "" {
		return fmt.Errorf("home directory is required")
	}
	if opts.Stdout == nil {
		opts.Stdout = io.Discard
	}
	if opts.Stdin == nil {
		opts.Stdin = os.Stdin
	}
	if opts.BuildDir == "" {
		opts.BuildDir = filepath.Join(opts.RepoRoot, "build")
	}
	if !filepath.IsAbs(opts.BuildDir) {
		opts.BuildDir = filepath.Join(opts.RepoRoot, opts.BuildDir)
	}

	reader := bufio.NewReader(opts.Stdin)
	interactiveTargetSelection := false
	if !opts.InstallClaude && !opts.InstallOpenCode {
		interactiveTargetSelection = true
		selection, err := selectTargets(reader, opts.Stdout)
		if err != nil {
			return err
		}
		opts.InstallClaude = selection.claude
		opts.InstallOpenCode = selection.opencode
	}

	if opts.ChatGPTProvider != "" && !validProvider(opts.ChatGPTProvider) {
		return fmt.Errorf("invalid ChatGPT provider %q", opts.ChatGPTProvider)
	}
	if interactiveTargetSelection && opts.InstallOpenCode && !opts.WorkMode && !opts.SkipBuild && opts.ChatGPTProvider == "" {
		provider, err := selectProvider(reader, opts.Stdout)
		if err != nil {
			return err
		}
		opts.ChatGPTProvider = provider
	}
	if opts.ChatGPTProvider == "" {
		opts.ChatGPTProvider = defaultProvider
	}

	if !opts.SkipBuild {
		if err := buildsys.Run(buildsys.Options{
			RepoRoot:        opts.RepoRoot,
			OutputDir:       opts.BuildDir,
			WorkMode:        opts.WorkMode,
			ChatGPTProvider: opts.ChatGPTProvider,
			Stdout:          opts.Stdout,
		}); err != nil {
			return err
		}
	}

	if _, err := os.Stat(opts.BuildDir); err != nil {
		return fmt.Errorf("build directory %s is not available: %w", opts.BuildDir, err)
	}

	fmt.Fprintln(opts.Stdout, "Install plan")
	fmt.Fprintf(opts.Stdout, "- build dir: %s\n", opts.BuildDir)
	if opts.SkipBuild {
		fmt.Fprintln(opts.Stdout, "- build step: skipped")
	} else {
		fmt.Fprintln(opts.Stdout, "- build step: executed")
	}
	if opts.WorkMode {
		fmt.Fprintln(opts.Stdout, "- model mode: work mappings")
	} else {
		fmt.Fprintf(opts.Stdout, "- ChatGPT provider: %s\n", opts.ChatGPTProvider)
	}

	if opts.InstallClaude {
		if err := installClaude(opts, reader); err != nil {
			return err
		}
	}
	if opts.InstallOpenCode {
		if err := installOpenCode(opts, reader); err != nil {
			return err
		}
	}

	return replayUnmappedModels(opts.BuildDir, opts.Stdout)
}

type targetSelection struct {
	claude   bool
	opencode bool
}

func selectTargets(reader *bufio.Reader, stdout io.Writer) (targetSelection, error) {
	fmt.Fprintln(stdout, "Select install target:")
	fmt.Fprintln(stdout, "  1) OpenCode only")
	fmt.Fprintln(stdout, "  2) Claude Code only")
	fmt.Fprintln(stdout, "  3) Both")
	choice, err := prompt(reader, stdout, "Choice [1/2/3]: ")
	if err != nil {
		return targetSelection{}, err
	}
	switch choice {
	case "1":
		return targetSelection{opencode: true}, nil
	case "2":
		return targetSelection{claude: true}, nil
	default:
		return targetSelection{claude: true, opencode: true}, nil
	}
}

func selectProvider(reader *bufio.Reader, stdout io.Writer) (string, error) {
	fmt.Fprintln(stdout, "Select ChatGPT provider for OpenCode GPT models:")
	fmt.Fprintln(stdout, "  1) openai")
	fmt.Fprintln(stdout, "  2) opencode")
	fmt.Fprintln(stdout, "  3) github-copilot")
	choice, err := prompt(reader, stdout, "Choice [1/2/3]: ")
	if err != nil {
		return "", err
	}
	switch choice {
	case "2":
		return "opencode", nil
	case "3":
		return "github-copilot", nil
	default:
		return defaultProvider, nil
	}
}

func installClaude(opts Options, reader *bufio.Reader) error {
	target := filepath.Join(opts.HomeDir, ".claude")

	agents, err := copyMarkdownDir(filepath.Join(opts.BuildDir, "claude", "agents"), filepath.Join(target, "agents"), "agents", opts, reader)
	if err != nil {
		return err
	}
	commands, err := copyMarkdownDir(filepath.Join(opts.BuildDir, "claude", "commands"), filepath.Join(target, "commands"), "commands", opts, reader)
	if err != nil {
		return err
	}
	skills, err := copyChildDirs(filepath.Join(opts.BuildDir, "claude", "skills"), filepath.Join(target, "skills"), "skills", opts, reader)
	if err != nil {
		return err
	}
	if _, err := copyWithOverwrite(filepath.Join(opts.BuildDir, "claude", "CLAUDE.md"), filepath.Join(target, "CLAUDE.md"), "CLAUDE.md", opts, reader); err != nil {
		return err
	}

	fmt.Fprintln(opts.Stdout, "Claude Code")
	fmt.Fprintf(opts.Stdout, "- target: %s\n", target)
	fmt.Fprintf(opts.Stdout, "- agents: %d\n", agents)
	fmt.Fprintf(opts.Stdout, "- commands: %d\n", commands)
	fmt.Fprintf(opts.Stdout, "- skills: %d\n", skills)
	fmt.Fprintln(opts.Stdout, "- base instructions: updated")
	return nil
}

func installOpenCode(opts Options, reader *bufio.Reader) error {
	target := filepath.Join(opts.HomeDir, ".config", "opencode")

	agents, err := copyMarkdownDir(filepath.Join(opts.BuildDir, "opencode", "agent"), filepath.Join(target, "agent"), "agent", opts, reader)
	if err != nil {
		return err
	}
	commands, err := copyMarkdownDir(filepath.Join(opts.BuildDir, "opencode", "command"), filepath.Join(target, "command"), "command", opts, reader)
	if err != nil {
		return err
	}
	skills, err := copyChildDirs(filepath.Join(opts.BuildDir, "opencode", "skill"), filepath.Join(target, "skill"), "skill", opts, reader)
	if err != nil {
		return err
	}
	if _, err := copyWithOverwrite(filepath.Join(opts.BuildDir, "opencode", "AGENTS.md"), filepath.Join(target, "AGENTS.md"), "AGENTS.md", opts, reader); err != nil {
		return err
	}

	fmt.Fprintln(opts.Stdout, "OpenCode")
	fmt.Fprintf(opts.Stdout, "- target: %s\n", target)
	fmt.Fprintf(opts.Stdout, "- agents: %d\n", agents)
	fmt.Fprintf(opts.Stdout, "- commands: %d\n", commands)
	fmt.Fprintf(opts.Stdout, "- skills: %d\n", skills)
	fmt.Fprintln(opts.Stdout, "- base instructions: updated")
	return nil
}

func copyMarkdownDir(srcDir, dstDir, label string, opts Options, reader *bufio.Reader) (int, error) {
	entries, err := os.ReadDir(srcDir)
	if err != nil {
		if os.IsNotExist(err) {
			return 0, nil
		}
		return 0, fmt.Errorf("read %s: %w", srcDir, err)
	}
	var names []string
	for _, entry := range entries {
		if entry.IsDir() || filepath.Ext(entry.Name()) != ".md" {
			continue
		}
		names = append(names, entry.Name())
	}
	sort.Strings(names)

	count := 0
	for _, name := range names {
		copied, err := copyWithOverwrite(filepath.Join(srcDir, name), filepath.Join(dstDir, name), label+"/"+name, opts, reader)
		if err != nil {
			return 0, err
		}
		if copied {
			count++
		}
	}
	return count, nil
}

func copyChildDirs(srcDir, dstDir, label string, opts Options, reader *bufio.Reader) (int, error) {
	entries, err := os.ReadDir(srcDir)
	if err != nil {
		if os.IsNotExist(err) {
			return 0, nil
		}
		return 0, fmt.Errorf("read %s: %w", srcDir, err)
	}
	var names []string
	for _, entry := range entries {
		if entry.IsDir() {
			names = append(names, entry.Name())
		}
	}
	sort.Strings(names)

	count := 0
	for _, name := range names {
		copied, err := copyWithOverwrite(filepath.Join(srcDir, name), filepath.Join(dstDir, name), label+"/"+name, opts, reader)
		if err != nil {
			return 0, err
		}
		if copied {
			count++
		}
	}
	return count, nil
}

func copyWithOverwrite(src, dst, label string, opts Options, reader *bufio.Reader) (bool, error) {
	info, err := os.Stat(src)
	if err != nil {
		if os.IsNotExist(err) {
			return false, nil
		}
		return false, fmt.Errorf("stat source %s: %w", src, err)
	}

	if _, err := os.Lstat(dst); err == nil {
		overwrite := opts.Force
		if !overwrite {
			answer, err := prompt(reader, opts.Stdout, fmt.Sprintf("Overwrite %s? [y/N]: ", label))
			if err != nil {
				return false, err
			}
			overwrite = strings.EqualFold(answer, "y")
		}
		if !overwrite {
			fmt.Fprintf(opts.Stdout, "Skipped %s\n", label)
			return false, nil
		}
		if err := os.RemoveAll(dst); err != nil {
			return false, fmt.Errorf("remove existing %s: %w", dst, err)
		}
	} else if err != nil && !os.IsNotExist(err) {
		return false, fmt.Errorf("stat destination %s: %w", dst, err)
	}

	if info.IsDir() {
		if err := files.CopyDir(src, dst); err != nil {
			return false, err
		}
	} else {
		if err := files.CopyFile(src, dst); err != nil {
			return false, err
		}
	}
	return true, nil
}

func replayUnmappedModels(buildDir string, stdout io.Writer) error {
	path := filepath.Join(buildDir, ".unmapped-models")
	raw, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return fmt.Errorf("read unmapped models %s: %w", path, err)
	}
	trimmed := strings.TrimSpace(string(raw))
	if trimmed == "" {
		return nil
	}
	fmt.Fprintln(stdout, "Unmapped models:")
	for _, line := range strings.Split(trimmed, "\n") {
		fmt.Fprintf(stdout, "- %s\n", line)
	}
	return nil
}

func prompt(reader *bufio.Reader, stdout io.Writer, message string) (string, error) {
	fmt.Fprint(stdout, message)
	text, err := reader.ReadString('\n')
	if err != nil && err != io.EOF {
		return "", err
	}
	return strings.TrimSpace(text), nil
}

func validProvider(provider string) bool {
	switch provider {
	case "openai", "opencode", "github-copilot":
		return true
	default:
		return false
	}
}
