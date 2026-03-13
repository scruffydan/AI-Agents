package prompts

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

var includePattern = regexp.MustCompile(`\{\{include:([^}]+)\}\}`)

func expandIncludes(body, dir string, stack []string) (string, error) {
	matches := includePattern.FindAllStringSubmatchIndex(body, -1)
	if len(matches) == 0 {
		return body, nil
	}

	var builder strings.Builder
	last := 0
	for _, match := range matches {
		start, end := match[0], match[1]
		fileStart, fileEnd := match[2], match[3]
		includeFile := body[fileStart:fileEnd]

		builder.WriteString(body[last:start])

		if contains(stack, includeFile) {
			return "", fmt.Errorf("include cycle detected: %s", strings.Join(append(stack, includeFile), " -> "))
		}

		includePath := filepath.Join(dir, includeFile)
		content, err := os.ReadFile(includePath)
		if err != nil {
			return "", fmt.Errorf("read include %s: %w", includePath, err)
		}

		expanded, err := expandIncludes(string(content), dir, append(stack, includeFile))
		if err != nil {
			return "", err
		}
		builder.WriteString(expanded)
		last = end
	}

	builder.WriteString(body[last:])
	return builder.String(), nil
}

func contains(values []string, target string) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}
	return false
}
