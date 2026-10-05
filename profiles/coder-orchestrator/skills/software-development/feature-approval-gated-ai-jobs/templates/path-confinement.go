package jobs

import (
	"fmt"
	"path/filepath"
)

func Confined(root, candidate string) (string, error) {
	r, e := filepath.Abs(root)
	if e != nil {
		return "", e
	}
	c, e := filepath.Abs(candidate)
	if e != nil {
		return "", e
	}
	rel, e := filepath.Rel(r, c)
	if e != nil || rel == ".." || len(rel) >= 3 && rel[:3] == ".."+string(filepath.Separator) {
		return "", fmt.Errorf("path escapes workspace")
	}
	return c, nil
}
