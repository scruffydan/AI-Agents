package app

import (
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"ai-agents/internal/buildsys"
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
		return errors.New("install is not implemented yet")
	case "init-opencode":
		return errors.New("init-opencode is not implemented yet")
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

func printHelp(w io.Writer) {
	fmt.Fprintln(w, "Usage: ai-agents <command> [options]")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Commands:")
	fmt.Fprintln(w, "  build          Generate Claude Code and OpenCode artifacts")
	fmt.Fprintln(w, "  install        Install generated artifacts (coming next)")
	fmt.Fprintln(w, "  init-opencode  Install opencode.json (coming next)")
}
