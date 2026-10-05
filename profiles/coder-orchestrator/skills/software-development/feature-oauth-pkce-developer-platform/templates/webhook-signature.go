package webhooks

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
)

func Sign(secret []byte, timestamp string, body []byte) string {
	m := hmac.New(sha256.New, secret)
	m.Write([]byte(timestamp))
	m.Write([]byte("."))
	m.Write(body)
	return hex.EncodeToString(m.Sum(nil))
}
func Verify(secret []byte, timestamp string, body []byte, signature string) bool {
	want, e := hex.DecodeString(signature)
	if e != nil {
		return false
	}
	got, e := hex.DecodeString(Sign(secret, timestamp, body))
	return e == nil && hmac.Equal(got, want)
}
