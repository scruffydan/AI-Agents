package app

import (
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"ai-agents/internal/buildsys"
	"ai-agents/internal/install"
)

func Run(args []string, stdout io.Writer, stderr io.Writer) error {
	if len(args) == 0 {
		printHelp(stdout)
		return nil
	}

	switch args[0] {
	case "build":
		return runBuild(args[1:], stdout)
	case "install":
		return runInstall(args[1:], stdout)
	case "init-opencode":
		return runInitOpenCode(args[1:], stdout)
	case "-h", "--help", "help":
		printHelp(stdout)
		return nil
	default:
		printHelp(stderr)
		return fmt.Errorf("unknown command %q", args[0])
	}
}

func runBuild(args []string, stdout io.Writer) error {
	wd, err := os.Getwd()
	if err != nil {
		return fmt.Errorf("get working directory: %w", err)
	}

	fs := flag.NewFlagSet("build", flag.ContinueOnError)
	fs.SetOutput(stdout)

	workMode := fs.Bool("work", false, "use work environment model mappings")
	chatgptProvider := fs.String("chatgpt-provider", "openai", "normalize OpenCode GPT models to openai, opencode, or github-copilot")
	outputDir := fs.String("output-dir", filepath.Join(wd, "build"), "write generated files to this directory")

	if err := fs.Parse(args); err != nil {
		if err == flag.ErrHelp {
			return nil
		}
		return err
	}

	return buildsys.Run(buildsys.Options{
		RepoRoot:        wd,
		OutputDir:       *outputDir,
		WorkMode:        *workMode,
		ChatGPTProvider: *chatgptProvider,
		Stdout:          stdout,
	})
}

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

func runInitOpenCode(args []string, stdout io.Writer) error {
	wd, err := os.Getwd()
	if err != nil {
		return fmt.Errorf("get working directory: %w", err)
	}
	homeDir, err := os.UserHomeDir()
	if err != nil {
		return fmt.Errorf("get home directory: %w", err)
	}

	fs := flag.NewFlagSet("init-opencode", flag.ContinueOnError)
	fs.SetOutput(stdout)
	force := fs.Bool("yes", false, "overwrite existing opencode.json without prompting")
	forceShort := fs.Bool("y", false, "overwrite existing opencode.json without prompting")
	if err := fs.Parse(args); err != nil {
		if err == flag.ErrHelp {
			return nil
		}
		return err
	}

	return install.InitOpenCode(install.InitOptions{
		RepoRoot: wd,
		HomeDir:  homeDir,
		Force:    *force || *forceShort,
		Stdin:    os.Stdin,
		Stdout:   stdout,
	})
}

func printHelp(w io.Writer) {
	fmt.Fprintln(w, "Usage: ai-agents <command> [options]")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Commands:")
	fmt.Fprintln(w, "  build          Generate Claude Code and OpenCode artifacts")
	fmt.Fprintln(w, "  install        Install generated artifacts into your config directories")
	fmt.Fprintln(w, "  init-opencode  Install source/opencode.json into ~/.config/opencode")
}
