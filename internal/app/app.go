package app

import (
	"fmt"
	"io"
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
