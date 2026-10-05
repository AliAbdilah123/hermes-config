package oauth

import (
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
)

func VerifyS256(verifier, challenge string) bool {
	h := sha256.Sum256([]byte(verifier))
	got := base64.RawURLEncoding.EncodeToString(h[:])
	return subtle.ConstantTimeCompare([]byte(got), []byte(challenge)) == 1
}
