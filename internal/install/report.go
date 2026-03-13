package install

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

func writeInstallPlan(opts Options) {
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
