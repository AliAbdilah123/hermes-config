package publishing

import "context"

type Request struct {
	IdempotencyKey, Text string
	MediaURLs            []string
	ProviderAccountID    string
}
type Result struct{ ProviderID, Permalink string }
type PublishError struct {
	Code      string
	Retryable bool
	Err       error
}

func (e *PublishError) Error() string { return e.Err.Error() }

type Provider interface {
	Publish(context.Context, Request) (Result, error)
}
