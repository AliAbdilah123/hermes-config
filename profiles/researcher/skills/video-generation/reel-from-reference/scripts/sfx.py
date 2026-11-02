#!/usr/bin/env python3
"""Procedural SFX generator — no asset downloads, pure ffmpeg synthesis.

    python sfx.py out_dir whoosh hit riser click sub tick

Every file is 48 kHz stereo WAV, loudness-normalised (-20 LUFS, TP -3),
so the mix stage only needs volume automation per cue, never gain guessing.
"""
import subprocess, sys, pathlib

SR = 48000
LN = "loudnorm=I=-20:TP=-3:LRA=7"

# name -> (duration, [lavfi input sources], filter_complex graph)
RECIPES = {
    # band-passed pink noise with a swell envelope: air movement / transition
    "whoosh": (0.65, [f"anoisesrc=d=0.65:c=pink:r={SR}:a=0.9"],
               "bandpass=f=900:width_type=h:w=1400,"
               "volume='if(lt(t,0.35),t/0.35,max(0,(0.65-t)/0.30))':eval=frame,"
               "aformat=channel_layouts=stereo"),
    # low sine with exponential decay + bright noise transient: impact / accent
    "hit": (0.60,
            [f"sine=f=180:d=0.60:r={SR}", f"anoisesrc=d=0.06:c=white:r={SR}:a=0.5"],
            "[0:a]aeval='val(0)*exp(-9*t)'[s];"
            "[1:a]highpass=f=2500,aeval='val(0)*exp(-60*t)'[n];"
            "[s][n]amix=inputs=2:normalize=0,aformat=channel_layouts=stereo"),
    # rising noise + rising sine, both ramping: tension into a reveal
    "riser": (1.10,
              [f"anoisesrc=d=1.1:c=pink:r={SR}:a=0.7",
               f"sine=f=700:d=1.1:r={SR}"],
              "[0:a]highpass=f=900,lowpass=f=7000,"
              "volume='pow(t/1.1,2)':eval=frame[n];"
              "[1:a]volume='0.30*pow(t/1.1,2)':eval=frame[s];"
              "[n][s]amix=inputs=2:normalize=0,aformat=channel_layouts=stereo"),
    # very short bright transient: UI/cursor/text arrival
    "click": (0.09, [f"anoisesrc=d=0.09:c=white:r={SR}:a=0.6"],
              "bandpass=f=4200:width_type=h:w=2200,"
              "volume='exp(-40*t)':eval=frame,aformat=channel_layouts=stereo"),
    # 70 Hz boom: scene changes / chapter marks
    "sub": (1.20, [f"sine=f=70:d=1.2:r={SR}"],
            "volume='exp(-4.5*t)':eval=frame,aformat=channel_layouts=stereo"),
    # gated ticks (9/s): data, counting, typing texture
    "tick": (0.50, [f"anoisesrc=d=0.5:c=white:r={SR}:a=0.8"],
             "bandpass=f=3000:width_type=h:w=1500,"
             "volume='0.35*pow(abs(sin(2*PI*9*t)),8)':eval=frame,"
             "aformat=channel_layouts=stereo"),
}


def build(name: str, out_dir: pathlib.Path) -> pathlib.Path:
    dur, sources, graph = RECIPES[name]
    out = out_dir / f"{name}.wav"
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for s in sources:
        cmd += ["-f", "lavfi", "-i", s]
    cmd += ["-filter_complex", f"{graph},{LN}", "-t", str(dur),
            "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(out)]
    subprocess.run(cmd, check=True)
    return out


def peak(path: pathlib.Path) -> tuple[float, float]:
    """Return (duration, max_volume dB) — asserts the file is not silence."""
    r = subprocess.run(["ffmpeg", "-i", str(path), "-af", "volumedetect",
                        "-f", "null", "-"], capture_output=True, text=True)
    mx = [l.split("max_volume:")[1].strip() for l in r.stderr.splitlines()
          if "max_volume:" in l]
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True).stdout.strip()
    return float(d), float(mx[0].split()[0]) if mx else -99.0


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__); print("available:", ", ".join(RECIPES)); raise SystemExit(2)
    out_dir = pathlib.Path(sys.argv[1]); out_dir.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[2:]:
        if name not in RECIPES:
            print(f"skip unknown sfx: {name}"); continue
        p = build(name, out_dir)
        d, db = peak(p)
        assert db > -45, f"{p.name} is silent ({db} dB)"
        print(f"{p.stem + '.wav':12s} {d:5.2f}s  peak {db:6.1f} dB")


if __name__ == "__main__":
    main()