---
name: video-to-skill
description: Turn a video into a reusable agent skill. Takes a public YouTube link or a local video/audio file, extracts its spoken content (existing subtitles first, otherwise ffmpeg, mp3, then speech-to-text), then distills that content into a new, standards-compliant skill folder (SKILL.md + scripts + references) that any agent can use. Use this whenever the user shares a YouTube URL or a video/audio file and wants a skill, workflow, playbook, SOP, checklist or "agent instructions" built from it, or says things like "learn from this video", "make a skill from this tutorial", "turn this video into instructions for agents", even if they never say the word "skill".
---

# video-to-skill

Converts the knowledge in one video into a new skill that other agents can load and follow. Two stages: **(A) get the transcript reliably**, then **(B) write a skill from it** following the standard skill layout.

Why this is split into scripts + judgment: transcript extraction is deterministic and should be done by the bundled scripts (so every agent gets the same result); deciding what in a video is worth turning into instructions is judgment, so that part is yours.

## Ground rules (read first)

- **Ask, never assume.** If anything is unclear (which parts of the video matter, target skill name, language, whether to install a tool, what to do when a download fails), stop and ask the user directly. Do not guess and continue.
- **Never publish without approval.** Writing into a git repository (including `AGENT.md`) happens only after the user has seen the exact planned changes and said yes. See `references/git-publish.md`.
- **Do not bypass access controls.** If a video is private, age-restricted, geo-blocked or the host blocks downloading, report it and ask the user for a downloaded file. Do not use cookies, proxies or other workarounds unless the user explicitly provides and approves them.
- **Respect copyright.** The new skill must contain distilled procedures and your own wording, not long verbatim passages of the transcript. Keep any quote under 15 words and cite the video.

## Workflow

### 1. Confirm the input and the goal
Input is either a public YouTube URL or a path to a local video/audio file. Confirm with the user: what the resulting skill should help an agent do, and the output folder (default `./out`). If the user gave neither a goal nor a clear video, ask.

### 2. Check the environment
```bash
python3 scripts/check_env.py
```
It reports whether `ffmpeg`, `yt-dlp` (URLs only) and `faster-whisper` (speech-to-text) are present, and prints install commands for the detected OS. **If a required tool is missing, tell the user which one and ask permission before installing** (e.g. `pip install -U yt-dlp faster-whisper`, `apt install ffmpeg` / `brew install ffmpeg` / `winget install ffmpeg`). If you cannot install (no permission, no network), ask the user how to proceed.

### 3. Extract the content
```bash
python3 scripts/extract_content.py "<url-or-file>" --out ./out/work
```
The script tries, in order, and records which one worked in `manifest.json`:
1. **Direct text**: human-written subtitles (YouTube manual captions, or a sidecar `.srt/.vtt`, or an embedded subtitle stream in a local file).
2. **ffmpeg, mp3, then speech-to-text**: if no direct text exists, it extracts audio with ffmpeg to mono 16 kHz mp3 and transcribes with faster-whisper (default model `large-v3`, the most accurate local option; VAD filter on to cut hallucinations in silence).

Auto-generated YouTube captions are skipped by default because they are noticeably less accurate than Whisper; pass `--allow-auto-subs` only if the user prefers speed over accuracy. Useful flags: `--lang vi|en|...` (otherwise auto-detect), `--model medium` (for weak machines), `--force-asr`, `--keep-audio`. Run `--help` for all.

Outputs in the work folder: `transcript.txt` (clean text), `transcript.md` (with timestamps), `transcript.json` (segments), `manifest.json` (source, method, language, model, duration, warnings), plus `audio.mp3` if kept.

If the script fails, read the error, report it plainly to the user, and ask how to proceed. Do not retry blindly with different tricks.

### 4. Understand the video, then design the skill
Read `transcript.md` fully. Then decide with the user if anything is ambiguous:
- What reusable procedure, rules, commands, templates or checklists does the video actually teach?
- What would trigger an agent to need this skill (this becomes the `description`)?
- Which steps are deterministic enough to deserve a script in `scripts/`?

Videos contain filler, sponsor reads and tangents; leave them out. If the transcript is thin or inaccurate (see `manifest.json` warnings), say so instead of padding.

### 5. Write the new skill
Follow `references/skill-output-template.md` for the exact folder layout, frontmatter rules and a SKILL.md skeleton. Key points:
- Folder name is kebab-case; `SKILL.md` needs `name` and `description` frontmatter, and the description says both what it does and when to use it (be a little pushy so it triggers).
- Keep `SKILL.md` under ~500 lines; move detail into `references/`, deterministic work into `scripts/`.
- Explain *why* behind instructions rather than writing rigid ALL-CAPS rules.
- Include a source.md file inside the new skill's references folder with the video URL/title, extraction method and date, so the provenance is traceable. Keep the full transcript out of the skill unless the user asks for it.
- Write the skill in English (shared standard for all agents) unless the user says otherwise; reply to the user in their own language.

Then validate: `python3 scripts/validate_skill.py ./out/<new-skill-name>`.

### 6. Deliver and get review
Show the user the new folder tree and a short summary of what the skill does and which video parts it came from. Wait for feedback and iterate. If the `skill-creator` skill is available, you may use it for test prompts and description tuning.

### 7. Publishing (only if the user asks, only after approval)
If the user wants it in a git repository, follow `references/git-publish.md`: prepare a preview of every file to be added or changed (including `AGENT.md`), show it, and wait for an explicit yes before any commit or push.
