package prompts

import "fmt"

type PromptType string

const (
	PromptTypeSubagent PromptType = "subagent"
	PromptTypeCommand  PromptType = "command"
	PromptTypeMode     PromptType = "mode"
)

type PromptDoc struct {
	Name        string
	Description string
	Type        PromptType
	Body        string
	Claude      map[string]any
	OpenCode    map[string]any
	SourcePath  string
}

func GetString(values map[string]any, key string) string {
	if values == nil {
		return ""
	}
	value, ok := values[key]
	if !ok || value == nil {
		return ""
	}
	return fmt.Sprint(value)
}

func CloneMap(values map[string]any) map[string]any {
	return cloneMap(values)
}

func cloneMap(values map[string]any) map[string]any {
	if len(values) == 0 {
		return map[string]any{}
	}
	cloned := make(map[string]any, len(values))
	for key, value := range values {
		cloned[key] = cloneValue(value)
	}
	return cloned
}

func cloneValue(value any) any {
	switch typed := value.(type) {
	case map[string]any:
		return cloneMap(typed)
	case []any:
		cloned := make([]any, 0, len(typed))
		for _, item := range typed {
			cloned = append(cloned, cloneValue(item))
		}
		return cloned
	default:
		return typed
	}
}
