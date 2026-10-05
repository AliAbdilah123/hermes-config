package marketplace

type Role string
type Rule struct {
	From, Action, To string
	Roles            map[Role]bool
}

func Transition(rules []Rule, from, action string, role Role) (string, bool) {
	for _, r := range rules {
		if r.From == from && r.Action == action && r.Roles[role] {
			return r.To, true
		}
	}
	return "", false
}
