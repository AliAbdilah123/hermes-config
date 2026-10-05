package capture

import (
	"context"
	"errors"
	"sync"
	"time"
)

type Sample map[string]float64
type Sampler func(context.Context) (Sample, error)
type Manager struct {
	mu       sync.Mutex
	running  bool
	progress int
	latest   []Sample
}

func (m *Manager) Start(ctx context.Context, n int, interval time.Duration, s Sampler) error {
	m.mu.Lock()
	if m.running {
		m.mu.Unlock()
		return errors.New("capture active")
	}
	m.running = true
	m.progress = 0
	m.mu.Unlock()
	go func() {
		defer func() { m.mu.Lock(); m.running = false; m.mu.Unlock() }()
		ok := 0
		for i := 0; i < n; i++ {
			x, e := s(ctx)
			if e == nil {
				m.mu.Lock()
				m.latest = append(m.latest, x)
				m.mu.Unlock()
				ok++
			}
			m.mu.Lock()
			m.progress = (i + 1) * 100 / n
			m.mu.Unlock()
			if i+1 < n {
				select {
				case <-ctx.Done():
					return
				case <-time.After(interval):
				}
			}
		}
		_ = ok
	}()
	return nil
}
