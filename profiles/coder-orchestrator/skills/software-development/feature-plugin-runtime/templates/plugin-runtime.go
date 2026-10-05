package plugins

import (
	"context"
	"fmt"
)

type Manifest struct {
	ID       string
	Requires []string
}
type Plugin interface {
	Manifest() Manifest
	Register(context.Context, Context) error
}
type Context interface {
	Provide(string, any) error
	Require(string) (any, error)
}

func Resolve(ps []Plugin) ([]Plugin, error) {
	by := map[string]Plugin{}
	for _, p := range ps {
		id := p.Manifest().ID
		if id == "" || by[id] != nil {
			return nil, fmt.Errorf("duplicate/empty plugin %q", id)
		}
		by[id] = p
	}
	state := map[string]uint8{}
	out := []Plugin{}
	var visit func(string) error
	visit = func(id string) error {
		if state[id] == 1 {
			return fmt.Errorf("dependency cycle at %s", id)
		}
		if state[id] == 2 {
			return nil
		}
		p := by[id]
		if p == nil {
			return fmt.Errorf("missing plugin %s", id)
		}
		state[id] = 1
		for _, d := range p.Manifest().Requires {
			if err := visit(d); err != nil {
				return err
			}
		}
		state[id] = 2
		out = append(out, p)
		return nil
	}
	for id := range by {
		if err := visit(id); err != nil {
			return nil, err
		}
	}
	return out, nil
}
