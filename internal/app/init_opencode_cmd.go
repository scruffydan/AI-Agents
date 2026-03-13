package app

import (
	"flag"
	"fmt"
	"io"
	"os"

	"ai-agents/internal/install"
)

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
	fs.Usage = func() {
		printInitOpenCodeHelp(stdout, fs)
	}
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
