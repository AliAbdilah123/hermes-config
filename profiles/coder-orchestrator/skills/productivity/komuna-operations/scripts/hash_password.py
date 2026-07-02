"""Komuna password hashing — exact reproduction of Go implementation.

Usage:
    python3 hash_password.py mypassword
    python3 hash_password.py         # interactive prompt

The Go API uses: salt = randomHex(16), then sha256(salt + ":" + password) 120000x.
Stored format: hex_salt:hex_digest
"""
import hashlib, secrets, sys


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    buf = (salt + ":" + password).encode()
    for _ in range(120000):
        buf = hashlib.sha256(buf).digest()
    return f"{salt}:{buf.hex()}"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pw = sys.argv[1]
    else:
        pw = input("Password: ")
    print(hash_password(pw))
