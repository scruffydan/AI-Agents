package install

import (
	"bufio"
	"fmt"
	"path/filepath"
)

type targetSelection struct {
	claude   bool
	opencode bool
}

type targetConfig struct {
	name           string
	targetDir      string
	agentsSource   string
	agentsTarget   string
	commandsSource string
	commandsTarget string
	skillsSource   string
	skillsTarget   string
	baseSource     string
	baseTarget     string
	baseLabel      string
}

func installClaude(opts Options, reader *bufio.Reader) error {
	return installTarget(targetConfig{
		name:           "Claude Code",
		targetDir:      filepath.Join(opts.HomeDir, ".claude"),
		agentsSource:   filepath.Join(opts.BuildDir, "claude", "agents"),
		agentsTarget:   "agents",
		commandsSource: filepath.Join(opts.BuildDir, "claude", "commands"),
		commandsTarget: "commands",
		skillsSource:   filepath.Join(opts.BuildDir, "claude", "skills"),
		skillsTarget:   "skills",
		baseSource:     filepath.Join(opts.BuildDir, "claude", "CLAUDE.md"),
		baseTarget:     "CLAUDE.md",
		baseLabel:      "base instructions",
	}, opts, reader)
}

func installOpenCode(opts Options, reader *bufio.Reader) error {
	return installTarget(targetConfig{
		name:           "OpenCode",
		targetDir:      filepath.Join(opts.HomeDir, ".config", "opencode"),
		agentsSource:   filepath.Join(opts.BuildDir, "opencode", "agent"),
		agentsTarget:   "agent",
		commandsSource: filepath.Join(opts.BuildDir, "opencode", "command"),
		commandsTarget: "command",
		skillsSource:   filepath.Join(opts.BuildDir, "opencode", "skill"),
		skillsTarget:   "skill",
		baseSource:     filepath.Join(opts.BuildDir, "opencode", "AGENTS.md"),
		baseTarget:     "AGENTS.md",
		baseLabel:      "base instructions",
	}, opts, reader)
}

func installTarget(config targetConfig, opts Options, reader *bufio.Reader) error {
	agents, err := copyMarkdownDir(config.agentsSource, filepath.Join(config.targetDir, config.agentsTarget), config.agentsTarget, opts, reader)
	if err != nil {
		return err
	}
	commands, err := copyMarkdownDir(config.commandsSource, filepath.Join(config.targetDir, config.commandsTarget), config.commandsTarget, opts, reader)
	if err != nil {
		return err
	}
	skills, err := copyChildDirs(config.skillsSource, filepath.Join(config.targetDir, config.skillsTarget), config.skillsTarget, opts, reader)
	if err != nil {
		return err
	}
	baseUpdated, err := copyWithOverwrite(config.baseSource, filepath.Join(config.targetDir, config.baseTarget), config.baseTarget, opts, reader)
	if err != nil {
		return err
	}

	fmt.Fprintln(opts.Stdout, config.name)
	fmt.Fprintf(opts.Stdout, "- target: %s\n", config.targetDir)
	fmt.Fprintf(opts.Stdout, "- agents: %d\n", agents)
	fmt.Fprintf(opts.Stdout, "- commands: %d\n", commands)
	fmt.Fprintf(opts.Stdout, "- skills: %d\n", skills)
	if baseUpdated {
		fmt.Fprintf(opts.Stdout, "- %s: updated\n", config.baseLabel)
	} else {
		fmt.Fprintf(opts.Stdout, "- %s: unchanged\n", config.baseLabel)
	}
	return nil
}
