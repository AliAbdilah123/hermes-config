YouTube downloads fail on this host's datacenter IP ("Sign in to confirm you're not a bot") regardless of yt-dlp player_client or JS runtime; requires user-supplied cookies.txt or an uploaded .mp4.
§
OpenDesign repo is cloned at ~/videos/open-design (design-systems/*/DESIGN.md + skills/ + video templates); Remotion deps are installed in ~/videos/node_modules and reusable by new projects via symlink.
§
OmniVoice + faster-whisper live in ~/.venvs/omnivoice (CPU torch wheel); HF weights cached at ~/.cache/hf-omnivoice (~3.2 GB). No GPU on this host — OmniVoice runs ~17x realtime at num_step=16.
§
OmniVoice TTS (k2-fsa, 3.2GB) runs CPU-only on this host via ~/.venvs/omnivoice; ~17x realtime at num_step=16, ~8.7x at 8. Always run in background, never a 600s foreground call. HF_HOME pinned to ~/.cache/hf-omnivoice.
§
faster-whisper (int8, CPU) is the working transcription path on this host; 'whisper' CLI is not installed.