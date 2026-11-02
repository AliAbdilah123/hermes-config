# OmniVoice (k2-fsa) — usable surface

Zero-shot multilingual TTS, 600+ languages, diffusion-LM architecture.
PyPI package `omnivoice`, model `k2-fsa/OmniVoice` on HF.

## Install (CPU-first, this is the order that works)

```bash
uv venv ~/.venvs/omnivoice --python 3.11
uv pip install --python ~/.venvs/omnivoice/bin/python \
  --index-url https://download.pytorch.org/whl/cpu torch torchaudio
uv pip install --python ~/.venvs/omnivoice/bin/python omnivoice faster-whisper
```

- Install torch from the **CPU index first**. Letting `omnivoice` resolve
  torch pulls the CUDA build (~2.5 GB of libs) on a machine with no GPU.
- `requires_dist` does **not** list `fastapi`/`uvicorn` even though
  `omnivoice-demo` needs them. Verify `python -c "import fastapi, uvicorn"`
  before planning a FastAPI UI on that env; if absent, install explicitly.
- Weights total ~3.2 GB (`model.safetensors` 2.45 GB + `audio_tokenizer`
  0.8 GB + tokenizer 11 MB) and are cached under `$HF_HOME`. Set
  `export HF_HOME=~/.cache/hf-omnivoice` once, or you re-download per cache dir.
- HF download from a datacenter IP runs ~19 MB/s — the 3.2 GB pull is a few
  minutes, fine, but do it as a background job, not inside a skill dry-run.

## Python API

```python
from omnivoice import OmniVoice
import torch, soundfile as sf

m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
audio = m.generate(text="...", instruct="male, low pitch")   # list[np.ndarray], 24 kHz
sf.write("out.wav", audio[0], 24000)
```

Three modes, same `generate()`:

| mode | arg | note |
|---|---|---|
| voice cloning | `ref_audio=`, `ref_text=` | best quality; omit `ref_text` to auto-ASR it. **Consent required.** |
| voice design | `instruct="female, low pitch, british accent"` | trained on zh/en only; no reference audio needed |
| auto voice | neither | random speaker, unstable across calls |

Reusable clone: `prompt = m.create_voice_clone_prompt(...); prompt.save("v.pt")`
then `VoiceClonePrompt.load("v.pt")` → `generate(voice_clone_prompt=prompt)`.
Skips re-encoding per call — worth it for a 5-scene reel.

Generation parameters worth setting:

- `num_step` (default 32): **16** is the quality/time sweet spot, **8** halves
  the cost again with mild artifacts. Use 8 for drafts, 16 for finals.
- `speed` (>1 faster), `duration=` (fixed seconds, overrides speed).
- `normalize_text=True` for Arabic numerals ("2048" → "two thousand forty-eight");
  needs `omnivoice[tn]` (WeTextProcessing). Latin-Indonesian numbers are safer
  spelled out in the script than relying on this.
- Inline non-verbals: `[laughter]`, `[sigh]`, `[surprise-oh]` etc.
- 3–10 s reference clip is the sweet spot for cloning; longer is slower and
  no better. Cross-lingual cloning carries the reference's accent.

## Measured CPU numbers (2 vCPU, no GPU, torch 2.15+cpu)

| what | value |
|---|---|
| cold model load | ~56 s |
| RTF @ num_step=16 | ~17× realtime (3.7 s audio ≈ 63 s) |
| RTF @ num_step=8 | ~8.7× realtime (3.7 s audio ≈ 32 s) |
| 5-scene reel (22.5 s narration) | several minutes @ step=16 |

Plan accordingly: batch a whole script in **one** process (model load is paid
once), write each wav as it completes so a crash doesn't lose the run, and
always run it backgrounded with completion notification.

## CLI equivalents

```bash
omnivoice-infer --model k2-fsa/OmniVoice --text "..." --output hello.wav \
  [--ref_audio ref.wav --ref_text "..."] [--instruct "male, british accent"]
omnivoice-infer-batch --test_list test.jsonl --res_dir results/   # multi-GPU
omnivoice-demo --ip 127.0.0.1 --port 8001                          # gradio UI
```

Batch JSONL needs only `id` + `text`; optional `ref_audio`, `ref_text`,
`instruct`, `language_id`, `duration`, `speed`.

## Ethics

Cloning someone else's voice without consent is out, full stop. Default to
`instruct` voice design; only take a `ref_audio` the user explicitly supplies
as their own or licensed.