#!/usr/bin/env python3
"""Assert a finished reel meets the delivery spec. Exit 1 on any failure.

    python verify.py ~/videos/my-reel          # or pass the mp4 directly

Checks only what can be checked mechanically. A human/vision pass still has to
read the subtitles and judge the composition.
"""
import json
import pathlib
import subprocess
import sys

W, H, FPS, SR = 1080, 1920, 30, 48000
TOL = 0.05  # seconds; one frame at 30fps is 0.033


def probe(path: pathlib.Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels"
         ":format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudness(path: pathlib.Path) -> tuple[float, float]:
    r = subprocess.run(["ffmpeg", "-i", str(path), "-af", "volumedetect",
                        "-f", "null", "-"], capture_output=True, text=True)
    mean = mx = -99.0
    for line in r.stderr.splitlines():
        if "mean_volume:" in line:
            mean = float(line.split("mean_volume:")[1].split("dB")[0])
        if "max_volume:" in line:
            mx = float(line.split("max_volume:")[1].split("dB")[0])
    return mean, mx


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    target = pathlib.Path(sys.argv[1]).expanduser()
    project = target if target.is_dir() else target.parent.parent
    mp4 = target if target.suffix == ".mp4" else None
    if mp4 is None:
        finals = [p for p in (project / "out").glob("*.mp4") if p.name != "video.mp4"]
        if not finals:
            print(f"FAIL no final mp4 in {project/'out'}")
            return 1
        mp4 = max(finals, key=lambda p: p.stat().st_mtime)

    fails, checks = [], []

    def check(ok: bool, msg: str) -> None:
        (checks if ok else fails).append(msg)

    info = probe(mp4)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"]["duration"])

    check(v is not None, "video stream present")
    if v:
        check(v["codec_name"] == "h264", f"video codec h264 (got {v['codec_name']})")
        check((v["width"], v["height"]) == (W, H),
              f"dimensions {W}x{H} (got {v['width']}x{v['height']})")
        check(v["r_frame_rate"] == f"{FPS}/1",
              f"fps {FPS} (got {v['r_frame_rate']})")

    check(a is not None, "audio stream present")
    if a:
        check(a["codec_name"] == "aac", f"audio codec aac (got {a['codec_name']})")
        check(int(a["sample_rate"]) == SR,
              f"audio {SR} Hz (got {a['sample_rate']})")
        check(a["channels"] == 2, f"stereo (got {a['channels']} ch)")

    mean, mx = loudness(mp4)
    check(-20.0 <= mean <= -14.0, f"mean volume {mean:.1f} dB in [-20,-14]")
    check(mx <= -0.5, f"peak {mx:.1f} dB <= -0.5 dBTP")

    tl_path = project / "work" / "timeline.json"
    if tl_path.exists():
        tl = json.loads(tl_path.read_text())
        want = float(tl["duration"])
        check(abs(dur - want) <= TOL,
              f"duration {dur:.2f}s matches timeline {want:.2f}s")
        check(dur >= want - TOL,
              "audio not truncated (a short tail means apad was dropped)")
        # captions must be the authored words, ascending, inside the scene
        bad = []
        for sc in tl["scenes"]:
            last = sc["start"] - 1
            for c in sc["cues"]:
                if c["start"] < sc["start"] - TOL:
                    bad.append(f"{sc['id']} cue before scene start")
                if c["end"] < c["start"]:
                    bad.append(f"{sc['id']} cue end < start: {c['text']!r}")
                if c["start"] < last - 1e-6:
                    bad.append(f"{sc['id']} cues overlap at {c['text']!r}")
                last = c["start"]
        check(not bad, "cue timings monotonic and inside scenes"
              + ("" if not bad else f": {bad[:3]}"))
    else:
        checks.append("timeline.json absent — duration/sync checks skipped")

    for c in checks:
        print(f"  ok   {c}")
    for f in fails:
        print(f"  FAIL {f}")
    print(f"\n{mp4}  {dur:.2f}s  {mp4.stat().st_size/1048576:.1f} MB")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())