package app

import (
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"ai-agents/internal/buildsys"
)

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
	fs.Usage = func() {
		printBuildHelp(stdout, fs)
	}

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
