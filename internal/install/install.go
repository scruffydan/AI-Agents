package install

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"ai-agents/internal/buildsys"
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

	writeInstallPlan(opts)

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
