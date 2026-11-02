#!/usr/bin/env python3
"""Reel Studio — one-page UI to repeat the pipeline on the next video.

    ~/.venvs/omnivoice/bin/python -m uvicorn --app-dir <skill>/ui app:app --port 8770

FastAPI + a single HTML file, no build step, no node on the UI path. Jobs run
as subprocesses of scripts/reel.py so the CLI stays the single source of truth
(the UI never reimplements a stage).
"""
from __future__ import annotations

import json, os, pathlib, subprocess, sys, threading, time, uuid

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

SKILL = pathlib.Path(__file__).resolve().parent.parent
ROOT = pathlib.Path(os.environ.get("REEL_ROOT", pathlib.Path.home() / "videos"))
PY = os.environ.get("REEL_PY", sys.executable)
APP = FastAPI(title="Reel Studio")
app = APP          # uvicorn app:app — the target name must be lowercase
JOBS: dict[str, dict] = {}

STAGES = ["transcribe", "tts", "timeline", "render", "mix"]
STAGE_LABEL = {
    "ingest": "Ambil video referensi",
    "transcribe": "Whisper baca referensi",
    "tts": "OmniVoice bikin suara",
    "timeline": "Sync scene + caption",
    "render": "Remotion render",
    "mix": "Audio FX + loudness",
}


def project(slug: str) -> pathlib.Path:
    p = (ROOT / slug).resolve()
    if ROOT.resolve() not in p.parents and p != ROOT.resolve():
        raise HTTPException(400, "slug escapes REEL_ROOT")
    if not (p / "package.json").exists():
        raise HTTPException(404, f"{slug} is not a reel project")
    return p


def read(p, default=None):
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def spawn(cmds: list[list[str]]) -> str:
    """Run one or more reel.py invocations sequentially in one background job."""
    jid = uuid.uuid4().hex[:8]
    JOBS[jid] = {"id": jid, "cmds": cmds, "started": time.time(), "status": "running"}
    log = pathlib.Path(ROOT) / ".reel-jobs" / f"{jid}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    JOBS[jid]["log"] = str(log)

    def worker():
        rc = 0
        with log.open("w") as fh:
            for cmd in cmds:
                fh.write(f"$ reel.py {' '.join(cmd)}\n")
                fh.flush()
                p = subprocess.run([PY, str(SKILL / "scripts" / "reel.py"), *cmd],
                                   stdout=fh, stderr=subprocess.STDOUT, text=True,
                                   env={**os.environ, "PYTHONUNBUFFERED": "1"})
                rc = p.returncode
                if rc:
                    break
        JOBS[jid].update(status="done" if rc == 0 else "failed", ended=time.time())

    threading.Thread(target=worker, daemon=True).start()
    return jid


# ------------------------------------------------------------------ routes
@APP.get("/", response_class=HTMLResponse)
def index():
    return (pathlib.Path(__file__).parent / "index.html").read_text()


@APP.get("/api/projects")
def projects():
    out = []
    for d in sorted(ROOT.iterdir()) if ROOT.exists() else []:
        if not (d / "package.json").exists() or not (d / "work").is_dir():
            continue
        tl = read(d / "work" / "timeline.json", {}) or {}
        out.append({
            "slug": d.name,
            "title": tl.get("title", d.name),
            "duration": tl.get("duration"),
            "scenes": len(tl.get("scenes", [])),
            "hasScript": (d / "script.json").exists(),
            "hasAudio": (d / "work" / "say.json").exists(),
            "hasTimeline": bool(tl),
            "final": next((f.name for f in (d / "out").glob("*.mp4")
                           if f.name != "video.mp4"), None) if (d / "out").is_dir() else None,
        })
    return out


@APP.post("/api/projects")
def create(slug: str = Form(...)):
    slug = "".join(c for c in slug.lower().replace(" ", "-") if c.isalnum() or c in "-_")
    if not slug:
        raise HTTPException(400, "slug kosong")
    if (ROOT / slug).exists():
        raise HTTPException(409, f"{slug} sudah ada")
    jid = spawn([["init", slug]])
    return {"job": jid, "slug": slug}


@APP.get("/api/ref/{slug}")
def ref_analysis(slug: str):
    p = project(slug)
    return read(p / "work" / "ref.json") or JSONResponse(
        {"error": "belum transcribe"}, status_code=404)


@APP.get("/api/script/{slug}")
def get_script(slug: str):
    p = project(slug)
    sc = read(p / "script.json")
    if sc is None:
        raise HTTPException(404, "script.json belum ada")
    return sc


@APP.put("/api/script/{slug}")
async def put_script(slug: str, payload: dict):
    p = project(slug)
    if not isinstance(payload.get("scenes"), list) or not payload["scenes"]:
        raise HTTPException(400, "scenes wajib diisi")
    for sc in payload["scenes"]:
        for k in ("id", "kind", "say"):
            if not sc.get(k):
                raise HTTPException(400, f"scene {sc.get('id','?')} tidak punya {k}")
    (p / "script.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return {"ok": True, "scenes": len(payload["scenes"])}


@APP.post("/api/ingest/{slug}")
async def ingest(slug: str, url: str = Form(""), file: UploadFile | None = File(None)):
    p = project(slug)
    if file is not None and file.filename:
        dest = p / "work" / f"upload-{file.filename}"
        dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(await file.read())
        return {"job": spawn([["ingest", slug, str(dest)]])}
    if not url.strip():
        raise HTTPException(400, "kasih URL atau file")
    return {"job": spawn([["ingest", slug, url.strip()]])}


@APP.post("/api/run/{slug}")
def run_stage(slug: str, stages: str = Form("")):
    p = project(slug)
    wanted = [s for s in (stages.split(",") if stages else STAGES) if s in STAGES]
    if not wanted:
        raise HTTPException(400, "tidak ada stage valid")
    # stages run sequentially inside one job; each is idempotent on its own
    jid = spawn([[s, slug] for s in wanted])
    return {"job": jid, "stages": wanted}


@APP.get("/api/job/{jid}")
def job(jid: str):
    j = JOBS.get(jid)
    if not j:
        raise HTTPException(404, "job tidak ada")
    log = pathlib.Path(j["log"])
    tail = log.read_text()[-2500:] if log.exists() else ""
    done = [c[0] for c in j["cmds"]]
    return {"id": jid, "status": j["status"], "log": tail,
            "elapsed": round(time.time() - j["started"], 1), "stages": done}


@APP.get("/api/result/{slug}")
def result(slug: str):
    p = project(slug)
    f = next((x for x in (p / "out").glob("*.mp4") if x.name != "video.mp4"), None) \
        if (p / "out").is_dir() else None
    if not f:
        raise HTTPException(404, "belum ada hasil")
    return {"file": f.name, "size": f.stat().st_size,
            "url": f"/media/{slug}/{f.name}"}


@APP.get("/media/{slug}/{name}")
def media(slug: str, name: str):
    p = project(slug) / "out" / name
    if not p.exists() or p.suffix not in (".mp4", ".png", ".jpg"):
        raise HTTPException(404, "tidak ada")
    return FileResponse(p)


@APP.get("/stage-label")
def labels():
    return STAGE_LABEL
