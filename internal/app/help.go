package app

import (
	"flag"
	"fmt"
	"io"
)

func printHelp(w io.Writer) {
	fmt.Fprintln(w, "Usage: ai-agents <command> [options]")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Commands:")
	fmt.Fprintln(w, "  build          Generate Claude Code and OpenCode artifacts from source prompts")
	fmt.Fprintln(w, "  install        Build and install configs into ~/.claude and ~/.config/opencode")
	fmt.Fprintln(w, "  init-opencode  Install source/opencode.json into ~/.config/opencode")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Examples:")
	fmt.Fprintln(w, "  ai-agents build")
	fmt.Fprintln(w, "  ai-agents build --work --output-dir /tmp/ai-agents-build")
	fmt.Fprintln(w, "  ai-agents install --all --yes")
	fmt.Fprintln(w, "  ai-agents init-opencode --yes")
}

func printBuildHelp(w io.Writer, fs *flag.FlagSet) {
	fmt.Fprintln(w, "Usage: ai-agents build [options]")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Generate Claude Code and OpenCode artifacts from source prompts.")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Options:")
	fs.PrintDefaults()
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Examples:")
	fmt.Fprintln(w, "  ai-agents build")
	fmt.Fprintln(w, "  ai-agents build --work")
	fmt.Fprintln(w, "  ai-agents build --chatgpt-provider github-copilot")
	fmt.Fprintln(w, "  ai-agents build --output-dir /tmp/ai-agents-build")
}

func printInstallHelp(w io.Writer, fs *flag.FlagSet) {
	fmt.Fprintln(w, "Usage: ai-agents install [options]")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Build and install configs into the Claude Code and OpenCode config directories.")
	fmt.Fprintln(w, "If no target is specified, the command prompts for a destination.")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Options:")
	fs.PrintDefaults()
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Examples:")
	fmt.Fprintln(w, "  ai-agents install")
	fmt.Fprintln(w, "  ai-agents install --claude --yes")
	fmt.Fprintln(w, "  ai-agents install --opencode --chatgpt-provider opencode")
	fmt.Fprintln(w, "  ai-agents install --all --skip-build")
}

func printInitOpenCodeHelp(w io.Writer, fs *flag.FlagSet) {
	fmt.Fprintln(w, "Usage: ai-agents init-opencode [options]")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Install source/opencode.json into ~/.config/opencode/opencode.json.")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Options:")
	fs.PrintDefaults()
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Examples:")
	fmt.Fprintln(w, "  ai-agents init-opencode")
	fmt.Fprintln(w, "  ai-agents init-opencode --yes")
}
