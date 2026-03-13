package prompts

import (
	"encoding/json"
	"fmt"
	"os"
)

type ModelMappings struct {
	Models map[string]string `json:"models"`
}

func LoadModelMappings(path string) (ModelMappings, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return ModelMappings{}, fmt.Errorf("read model mappings %s: %w", path, err)
	}

	var mappings ModelMappings
	if err := json.Unmarshal(raw, &mappings); err != nil {
		return ModelMappings{}, fmt.Errorf("parse model mappings %s: %w", path, err)
	}
	if mappings.Models == nil {
		mappings.Models = map[string]string{}
	}
	return mappings, nil
}
