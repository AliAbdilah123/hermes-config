---
name: yt-dlp-download
description: "Download permitted YouTube videos or audio locally with yt-dlp."
version: 1.0.0
created_by: agent
platforms: [linux]
---

# yt-dlp downloads

## Use when
A user provides a YouTube URL and asks to download video, audio, subtitles, or metadata. Only download content the user is authorized to save and that complies with YouTube's terms and applicable law.

## Prerequisites
- `yt-dlp` is installed at `~/.local/bin/yt-dlp`.
- `ffmpeg` is installed for merging video/audio and converting audio.

## Commands
Create the target directory first. Preserve the video ID in filenames to avoid collisions.

```bash
mkdir -p ~/Downloads/youtube
~/.local/bin/yt-dlp --no-playlist -f 'bv*+ba/b' --merge-output-format mp4 \
  -o '~/Downloads/youtube/%(title).180B [%(id)s].%(ext)s' 'URL'
```

Audio-only MP3:

```bash
mkdir -p ~/Downloads/youtube
~/.local/bin/yt-dlp --no-playlist -x --audio-format mp3 --audio-quality 0 \
  -o '~/Downloads/youtube/%(title).180B [%(id)s].%(ext)s' 'URL'
```

Subtitles when available:

```bash
~/.local/bin/yt-dlp --no-playlist --write-subs --write-auto-subs --sub-langs 'en.*' --skip-download 'URL'
```

## Workflow
1. Ask whether the user wants video or audio only if unspecified; default to MP4 video.
2. Use `--no-playlist` unless they explicitly request every item in a playlist.
3. Run the command and report the real output path.
4. Verify the file exists and is non-empty: `test -s 'PATH'`.
5. If YouTube extraction warns about JavaScript runtime but succeeds, report nothing extra. If formats fail, explain that a supported JS runtime may be needed; do not claim success.

## Updating

```bash
uv tool upgrade yt-dlp
```
