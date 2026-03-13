package install

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"ai-agents/internal/files"
)

type InitOptions struct {
	RepoRoot string
	HomeDir  string
	Force    bool
	Stdin    io.Reader
	Stdout   io.Writer
}

func InitOpenCode(opts InitOptions) error {
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

	source := filepath.Join(opts.RepoRoot, "source", "opencode.json")
	target := filepath.Join(opts.HomeDir, ".config", "opencode", "opencode.json")
	reader := bufio.NewReader(opts.Stdin)

	if _, err := os.Stat(source); err != nil {
		return fmt.Errorf("stat source config %s: %w", source, err)
	}

	if _, err := os.Lstat(target); err == nil {
		if !opts.Force {
			answer, err := prompt(reader, opts.Stdout, "Overwrite existing opencode.json? [y/N]: ")
			if err != nil {
				return err
			}
			if answer != "y" && answer != "Y" {
				fmt.Fprintln(opts.Stdout, "OpenCode config unchanged")
				return nil
			}
		}
		if err := os.RemoveAll(target); err != nil {
			return fmt.Errorf("remove existing config %s: %w", target, err)
		}
	} else if err != nil && !os.IsNotExist(err) {
		return fmt.Errorf("stat target config %s: %w", target, err)
	}

	if err := files.CopyFile(source, target); err != nil {
		return err
	}

	fmt.Fprintf(opts.Stdout, "Installed OpenCode config to %s\n", target)
	return nil
}
