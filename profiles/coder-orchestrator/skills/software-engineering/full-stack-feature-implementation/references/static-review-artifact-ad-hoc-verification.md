# Static review artifact ad-hoc verification

Use this for standalone plan/design HTML changed during a full-stack feature workflow when no canonical document validator exists.

1. During creative iteration, wait until the user likes the direction or a commit is imminent.
2. Create an OS-safe temporary verifier with `mktemp /tmp/hermes-verify-<topic>-XXXXXX.py`.
3. Check changed artifacts for one balanced HTML root, viewport metadata, responsive `@media` CSS, balanced scripts, required theme-toggle persistence, and task-critical phrases/links/states.
4. Run it from the project root and remove it afterward.
5. Separately verify local/public HTTP 200 with cache busting when the artifact is published.
6. Report this only as “ad-hoc static artifact verification.” It is not application tests, build success, or suite-green evidence.

Minimal Python shape:

```python
from pathlib import Path

paths = [Path("docs/example-plan.html"), Path("docs/example-design.html")]
required = ["<!doctype html>", 'name="viewport"', "@media", "localStorage"]
for path in paths:
    text = path.read_text()
    missing = [item for item in required if item not in text]
    assert not missing, f"{path}: missing {missing}"
    assert text.count("<html") == text.count("</html>") == 1
    assert text.count("<script") == text.count("</script>")
print(f"ad-hoc HTML checks passed for {len(paths)} files")
```

Adapt required strings to the reviewed behavior. Keep one-off verifiers temporary; only stable project validators belong under project scripts.
