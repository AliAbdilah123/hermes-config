#!/usr/bin/env python3
"""reel.py — reference video -> original short-form video, one CLI.

Stages (each idempotent, all state in <project>/work):

  init      <dir>                      scaffold project from skill templates
  ingest    <dir> <url|file>           yt-dlp (or copy) -> work/source.mp4
  transcribe <dir>                     whisper -> work/ref.json (text + pacing)
  tts       <dir>                      OmniVoice per scene -> work/say/*.wav
  timeline  <dir>                      word-align narration -> work/timeline.json
  render    <dir>                      Remotion (video only) -> out/video.mp4
  mix       <dir>                      narration + SFX + loudnorm -> out/<slug>.mp4
  build     <dir>                      transcribe? tts timeline render mix

Design rule: the reference is *measured*, never imitated. `transcribe` emits
pacing statistics (words/s, hook length, scene count) which shape the original
script; nothing from the reference is replayed.
"""
from __future__ import annotations

import json, os, shutil, subprocess, sys, wave, pathlib, math

SKILL = pathlib.Path(__file__).resolve().parent.parent
SR = 48000
WHISPER = os.environ.get("REEL_WHISPER", "small")
PY = os.environ.get("REEL_PY", sys.executable)          # venv with torch+omnivoice
W = lambda d: pathlib.Path(d) / "work"


# ---------------------------------------------------------------- helpers
def run(cmd, **kw):
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if p.returncode:
        raise SystemExit(f"FAILED: {' '.join(map(str, cmd))}\n{p.stderr[-2500:]}")
    return p


def read_json(p):
    return json.loads(pathlib.Path(p).read_text())


def write_json(p, obj):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(p).write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def dur(p) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", p]).stdout.strip())


def slugify(s: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48] or "reel"


# ---------------------------------------------------------------- init
def cmd_init(project: str, **_):
    d = pathlib.Path(project)
    for rel in ("work", "public", "out", "src"):
        (d / rel).mkdir(parents=True, exist_ok=True)
    tpl = SKILL / "templates" / "remotion"
    for f in tpl.iterdir():
        if f.name == "package.json":
            continue
        dest = d / ("src" if f.suffix in (".ts", ".tsx") else "") / f.name
        if not dest.exists():
            shutil.copy(f, dest)
    if not (d / "package.json").exists():
        shutil.copy(tpl / "package.json", d / "package.json")
    if not (d / "node_modules").exists():          # reuse a shared install
        pool = pathlib.Path.home() / "videos" / "node_modules"
        if pool.exists():
            (d / "node_modules").symlink_to(pool)
    if not (d / "script.json").exists():
        shutil.copy(SKILL / "templates" / "script.json", d / "script.json")
    if not (d / "public" / "sfx").exists():
        run([PY, SKILL / "scripts" / "sfx.py", d / "public" / "sfx",
             "whoosh", "hit", "riser", "click", "sub"])
    print(f"initialised {d}")


# ---------------------------------------------------------------- ingest
def cmd_ingest(project: str, src: str, cookies: str = "", **_):
    d = pathlib.Path(project); out = W(project) / "source.mp4"
    if pathlib.Path(src).exists():
        run(["ffmpeg", "-y", "-v", "error", "-i", src, "-c", "copy", out])
    else:
        cmd = ["yt-dlp", "-f", "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080]",
               "--merge-output-format", "mp4", "-o", out, src]
        if cookies:
            cmd += ["--cookies", cookies]
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode:
            raise SystemExit(
                "yt-dlp failed. From a datacenter IP YouTube blocks with "
                "'Sign in to confirm you're not a bot' — that flag is on the IP, "
                "not the client: player_client tricks and JS runtimes do not help.\n"
                "Fix: pass --cookies cookies.txt (export from a logged-in browser), "
                "or upload the .mp4 and pass its path instead.\n\n"
                + p.stderr[-800:])
    audio = W(project) / "ref.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", out, "-vn", "-ac", "1",
         "-ar", "16000", "-c:a", "pcm_s16le", audio])
    print(f"source {dur(out):.1f}s -> {audio}")


# ---------------------------------------------------------------- transcribe
def cmd_transcribe(project: str, model: str = WHISPER, **_):
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device="cpu", compute_type="int8")
    segs, info = m.transcribe(str(W(project) / "ref.wav"), word_timestamps=True,
                              vad_filter=True, beam_size=5)
    segs = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
             "words": [{"t": round(w.start, 2), "w": w.word} for w in (s.words or [])]}
            for s in segs]
    total = segs[-1]["end"] if segs else 1.0
    words = sum(len(s["text"].split()) for s in segs)
    # pacing profile: what the reference does, as numbers to design *against*
    gaps = [b["start"] - a["end"] for a, b in zip(segs, segs[1:])]
    ref = {
        "language": info.language, "duration": round(total, 2),
        "words": words, "words_per_sec": round(words / total, 2),
        "mean_segment": round(total / max(len(segs), 1), 2),
        "mean_pause": round(sum(g for g in gaps if g > 0) / max(len(gaps), 1), 2),
        "suggested_scene": round(max(2.0, min(6.0, total / max(len(segs), 1))), 2),
        "transcript": segs,
    }
    write_json(W(project) / "ref.json", ref)
    print(f"{ref['language']} {total:.1f}s {words} words {ref['words_per_sec']} w/s "
          f"-> {W(project)/'ref.json'}")


# ---------------------------------------------------------------- tts
def cmd_tts(project: str, **_):
    import numpy as np, soundfile as sf, torch
    from omnivoice import OmniVoice
    d = pathlib.Path(project); script = read_json(d / "script.json")
    voice = script.get("voice", {})
    model = OmniVoice.from_pretrained(voice.get("model", "k2-fsa/OmniVoice"),
                                     device_map="cpu", dtype=torch.float32)
    say = W(project) / "say"; say.mkdir(parents=True, exist_ok=True)
    clone = voice.get("clone")          # optional ref wav; consent required
    prompt = None
    if clone:
        prompt = model.create_voice_clone_prompt(ref_audio=clone)
    out = []
    for sc in script["scenes"]:
        wav = say / f"{sc['id']}.wav"
        if not wav.exists():
            kw = dict(text=sc["say"], speed=float(voice.get("speed", 1.0)),
                      num_step=int(voice.get("steps", 16)))
            if prompt is not None:
                kw["voice_clone_prompt"] = prompt
            elif voice.get("instruct"):
                kw["instruct"] = voice["instruct"]
            a = model.generate(**kw)[0]
            sf.write(wav, a, 24000)
        out.append({"id": sc["id"], "file": f"work/say/{sc['id']}.wav",
                    "duration": round(dur(wav), 3)})
        print(f"  {sc['id']:10s} {out[-1]['duration']:6.2f}s")
    write_json(W(project) / "say.json", out)


# ---------------------------------------------------------------- timeline
def cmd_timeline(project: str, model: str = WHISPER, pad: float = 0.28, **_):
    """Scene durations come from the generated audio; captions from word timing."""
    from faster_whisper import WhisperModel
    d = pathlib.Path(project); script = read_json(d / "script.json")
    say = {s["id"]: s for s in read_json(W(project) / "say.json")}
    m = WhisperModel(model, device="cpu", compute_type="int8")
    scenes, t = [], 0.0
    for sc in script["scenes"]:
        a = say[sc["id"]]
        segs, _ = m.transcribe(str(d / a["file"]), word_timestamps=True,
                               language=script.get("lang"), vad_filter=False)
        words = [w for s in segs for w in (s.words or [])]
        cues = wrap_cues(words, sc["say"])
        length = a["duration"] + pad
        scenes.append({
            "id": sc["id"], "kind": sc["kind"], "kicker": sc.get("kicker", ""),
            "headline": sc.get("headline", ""), "body": sc.get("body", ""),
            "say": sc["say"], "audio": a["file"],
            "start": round(t, 3), "dur": round(length, 3),
            "fadeIn": 0.22, "pad": pad,
            "cues": [{"start": round(c["start"] + t, 3), "end": round(c["end"] + t, 3),
                      "text": c["text"]} for c in cues],
        })
        t += length
    tl = {"slug": slugify(script["title"]), "title": script["title"],
          "fps": 30, "width": 1080, "height": 1920, "duration": round(t, 3),
          "theme": script.get("theme", {}), "scenes": scenes}
    write_json(W(project) / "timeline.json", tl)
    print(f"{len(scenes)} scenes {t:.2f}s -> {W(project)/'timeline.json'}")


def wrap_cues(words, text, max_words=4, max_gap=0.7):
    """Use Whisper for TIMING only; take the WORDS from our own script.

    Whisper mis-transcribes TTS output ("videonya" -> "vidionya"). The script is
    ground truth, so cues are cut from `text` and mapped onto the word timings
    one-for-one. If the counts disagree (Whisper dropped or merged a word) we
    fall back to proportional slicing rather than showing wrong text.
    """
    tokens = text.split()
    if not words or not tokens:
        return [{"start": 0.0, "end": 99.0, "text": text}]

    cues = []
    n = len(tokens)
    k = len(words) / n
    for i in range(0, n, max_words):
        chunk = tokens[i:i + max_words]
        if len(words) == n:
            start, end = words[i].start, words[i + len(chunk) - 1].end
        else:
            start = words[min(int(i * k), len(words) - 1)].start
            end = words[min(int((i + len(chunk)) * k) - 1, len(words) - 1)].end
        cues.append({"start": start, "end": max(end, start + 0.35),
                     "text": " ".join(chunk)})
    return cues


# ---------------------------------------------------------------- render
def cmd_render(project: str, frames: str = "", **_):
    d = pathlib.Path(project).resolve()
    tl = W(project) / "timeline.json"
    seconds = read_json(tl)["duration"]
    # --props must be an ABSOLUTE path: Remotion resolves it against the CLI cwd.
    cmd = ["npx", "remotion", "render", "src/index.tsx", "Reel", "out/video.mp4",
           f"--props={tl.resolve()}", "--codec=h264", "--crf=20", "--concurrency=2",
           "--log=error"]
    if frames:
        cmd.append(f"--frames={frames}")
    run(cmd, cwd=d)
    print(f"video {dur(d/'out'/'video.mp4'):.2f}s (expected {seconds:.2f}s)")


# ---------------------------------------------------------------- mix
def cmd_mix(project: str, **_):
    """Narration + SFX in one ffmpeg graph, then loudnorm to social spec.

    Every path is resolved ABSOLUTE before the ffmpeg call. Mixing relative
    inputs with cwd=<project> is how you get `demo-reel/demo-reel/work/...`.
    """
    d = pathlib.Path(project).resolve()
    tl = read_json(W(project) / "timeline.json")

    inputs, labels = [], []
    for sc in tl["scenes"]:                       # bed: one narration file per scene
        inputs.append(d / sc["audio"])
        at = int(sc["start"] * 1000)
        labels.append(f"[{len(inputs)-1}:a]adelay={at}|{at},"
                      f"aformat=sample_rates={SR}:channel_layouts=stereo[n{len(labels)}]")
    for sc in tl["scenes"]:                       # accents: scene-relative, absolute time
        for name, offset, vol in sfx_cues(sc):
            inputs.append(d / "public" / "sfx" / f"{name}.wav")
            at = max(0, int((sc["start"] + offset) * 1000))
            labels.append(f"[{len(inputs)-1}:a]adelay={at}|{at},volume={vol}"
                          f"[s{len(labels)}]")

    bed = len(tl["scenes"])
    streams = "".join(f"[n{i}]" for i in range(bed)) + \
              "".join(f"[s{i}]" for i in range(bed, len(labels)))
    # apad is mandatory: amix ends at the last narration sample, so atrim alone
    # can never reach the timeline length and -shortest would clip the tail.
    graph = ";".join(labels) + \
            f";{streams}amix=inputs={len(labels)}:duration=longest:normalize=0," \
            f"apad,atrim=0:{tl['duration']},asetpts=N/SR/TB," \
            "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.95," \
            f"aresample={SR}[a]"

    cmd = ["ffmpeg", "-y", "-v", "error"]
    for p in inputs:
        cmd += ["-i", str(p)]
    mixwav = W(project).resolve() / "mix.wav"
    run(cmd + ["-filter_complex", graph, "-map", "[a]", "-c:a", "pcm_s16le",
               str(mixwav)])

    out = d / "out" / f"{tl['slug']}.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", d / "out" / "video.mp4",
         "-i", mixwav, "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
         "-movflags", "+faststart", str(out)])
    print(f"final {out} {dur(out):.2f}s  ({len(inputs)} audio streams)")


def sfx_cues(sc):
    """SFX design per scene kind — sparse on purpose: one accent per beat."""
    kind = sc["kind"]
    if kind == "hook":
        return [("riser", 0.0, 0.45), ("hit", max(0.2, sc["dur"] - 0.55), 0.5)]
    if kind == "end":
        return [("sub", 0.0, 0.55)]
    if kind == "stat":
        return [("whoosh", 0.0, 0.4), ("click", min(0.45, sc["dur"] / 3), 0.30)]
    return [("whoosh", 0.0, 0.32)]


# ---------------------------------------------------------------- build
def cmd_build(project: str, src: str = "", cookies: str = "", **_):
    if src:
        cmd_ingest(project, src, cookies)
    if (W(project) / "ref.wav").exists() and not (W(project) / "ref.json").exists():
        cmd_transcribe(project)
    for step in (cmd_tts, cmd_timeline, cmd_render, cmd_mix):
        if step is cmd_tts and (W(project) / "say.json").exists():
            continue
        step(project)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    args, kw = sys.argv[2:], {}
    pos = []
    for a in args:
        if "=" in a and not pathlib.Path(a).exists():
            k, v = a.split("=", 1); kw[k.replace("-", "_")] = v
        else:
            pos.append(a)
    fns = {k[4:]: v for k, v in globals().items() if k.startswith("cmd_")}
    if cmd not in fns:
        print(__doc__); print("commands:", ", ".join(fns)); raise SystemExit(2)
    fns[cmd](*pos, **kw)


if __name__ == "__main__":
    main()