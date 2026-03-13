package app

import (
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"ai-agents/internal/install"
)

func runInstall(args []string, stdout io.Writer) error {
	wd, err := os.Getwd()
	if err != nil {
		return fmt.Errorf("get working directory: %w", err)
	}
	homeDir, err := os.UserHomeDir()
	if err != nil {
		return fmt.Errorf("get home directory: %w", err)
	}

	fs := flag.NewFlagSet("install", flag.ContinueOnError)
	fs.SetOutput(stdout)

	force := fs.Bool("yes", false, "overwrite existing files without prompting")
	forceShort := fs.Bool("y", false, "overwrite existing files without prompting")
	installClaude := fs.Bool("claude", false, "install Claude Code config")
	installOpenCode := fs.Bool("opencode", false, "install OpenCode config")
	installAll := fs.Bool("all", false, "install both Claude Code and OpenCode")
	skipBuild := fs.Bool("skip-build", false, "reuse the existing build directory")
	workMode := fs.Bool("work", false, "use work environment model mappings")
	chatgptProvider := fs.String("chatgpt-provider", "", "normalize OpenCode GPT models to openai, opencode, or github-copilot")
	fs.Usage = func() {
		printInstallHelp(stdout, fs)
	}

	if err := fs.Parse(args); err != nil {
		if err == flag.ErrHelp {
			return nil
		}
		return err
	}

	if *installAll {
		*installClaude = true
		*installOpenCode = true
	}

	return install.Run(install.Options{
		RepoRoot:        wd,
		BuildDir:        filepath.Join(wd, "build"),
		HomeDir:         homeDir,
		InstallClaude:   *installClaude,
		InstallOpenCode: *installOpenCode,
		SkipBuild:       *skipBuild,
		WorkMode:        *workMode,
		Force:           *force || *forceShort,
		ChatGPTProvider: *chatgptProvider,
		Stdin:           os.Stdin,
		Stdout:          stdout,
	})
}
