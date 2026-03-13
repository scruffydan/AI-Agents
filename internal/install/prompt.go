package install

import (
	"bufio"
	"fmt"
	"io"
	"strings"
)

func selectTargets(reader *bufio.Reader, stdout io.Writer) (targetSelection, error) {
	fmt.Fprintln(stdout, "Select install target:")
	fmt.Fprintln(stdout, "  1) OpenCode only")
	fmt.Fprintln(stdout, "  2) Claude Code only")
	fmt.Fprintln(stdout, "  3) Both")
	choice, err := prompt(reader, stdout, "Choice [1/2/3]: ")
	if err != nil {
		return targetSelection{}, err
	}
	switch choice {
	case "1":
		return targetSelection{opencode: true}, nil
	case "2":
		return targetSelection{claude: true}, nil
	default:
		return targetSelection{claude: true, opencode: true}, nil
	}
}

func selectProvider(reader *bufio.Reader, stdout io.Writer) (string, error) {
	fmt.Fprintln(stdout, "Select ChatGPT provider for OpenCode GPT models:")
	fmt.Fprintln(stdout, "  1) openai")
	fmt.Fprintln(stdout, "  2) opencode")
	fmt.Fprintln(stdout, "  3) github-copilot")
	choice, err := prompt(reader, stdout, "Choice [1/2/3]: ")
	if err != nil {
		return "", err
	}
	switch choice {
	case "2":
		return "opencode", nil
	case "3":
		return "github-copilot", nil
	default:
		return defaultProvider, nil
	}
}

func prompt(reader *bufio.Reader, stdout io.Writer, message string) (string, error) {
	fmt.Fprint(stdout, message)
	text, err := reader.ReadString('\n')
	if err != nil && err != io.EOF {
		return "", err
	}
	return strings.TrimSpace(text), nil
}

func validProvider(provider string) bool {
	switch provider {
	case "openai", "opencode", "github-copilot":
		return true
	default:
		return false
	}
}
