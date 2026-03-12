# Artifact Types

All 9 artifact types supported by NotebookLM Studio via `notebooklm` CLI.

## Overview

| # | Type | CLI Generate | Sync? | Est. Time | Download Format |
|---|------|-------------|-------|-----------|-----------------|
| 1 | Audio (Podcast) | `generate audio` | Async | 5-30 min | MP3 |
| 2 | Video | `generate video` | Async | 5-30 min | MP4 |
| 3 | Report | `generate report` | Async | 1-2 min | Markdown |
| 4 | Quiz | `generate quiz` | Async | 1-2 min | JSON/MD/HTML |
| 5 | Flashcards | `generate flashcards` | Async | 1-2 min | JSON/MD/HTML |
| 6 | Mind Map | `generate mind-map` | **SYNC** | Instant | JSON |
| 7 | Slide Deck | `generate slide-deck` | Async | 2-10 min | PDF/PPTX |
| 8 | Infographic | `generate infographic` | Async | 2-5 min | PNG |
| 9 | Data Table | `generate data-table` | Async | 1-2 min | CSV |

---

## 1. Audio (Podcast)

Generate an audio overview (podcast-style conversation).

**Generate:**
```bash
notebooklm generate audio [description] \
  --format [deep-dive|brief|critique|debate] \
  --length [short|default|long] \
  --language LANG \
  -s SOURCE_ID \
  --wait
```

**Download:**
```bash
notebooklm download audio ./output/<slug>/podcast.mp3
```

**Options:**
- `--format`: deep-dive (default), brief, critique, debate
- `--length`: short, default, long
- `--language`: Language code (default: en)
- `-s/--source`: Select specific sources (repeatable)

**Notes:**
- Longest generation time (5-30 min)
- **Tier 2 artifact** — in agent mode, use `--json` instead of `--wait` for non-blocking generation. See "Deferred Generation" below.
- Post-process with `scripts/compress_audio.sh` for Telegram 50MB limit
- Default download format is MP4 container; rename to .mp3 as needed

---

## 2. Video

Generate a video overview with visual styles.

**Generate:**
```bash
notebooklm generate video [description] \
  --format [explainer|brief|cinematic] \
  --style [auto|classic|whiteboard|kawaii|anime|watercolor|retro-print|heritage|paper-craft] \
  --language LANG \
  -s SOURCE_ID \
  --wait
```

Alias for cinematic format:
```bash
notebooklm generate cinematic-video [description] --wait
```

**Download:**
```bash
notebooklm download video ./output/<slug>/video.mp4
```

**Options:**
- `--format`: explainer, brief, cinematic
- `--style`: 9 visual styles (auto, classic, whiteboard, kawaii, anime, watercolor, retro-print, heritage, paper-craft)
- `--language`: Language code

**Notes:**
- Generation time similar to audio (5-30 min)
- **Tier 2 artifact** — in agent mode, use `--json` instead of `--wait` for non-blocking generation. See "Deferred Generation" below.
- Check file size for Telegram 50MB limit (no compression script available)

---

## 3. Report

Generate a text report in various formats.

**Generate:**
```bash
notebooklm generate report [description] \
  --format [briefing-doc|study-guide|blog-post|custom] \
  --append "extra instructions" \
  -s SOURCE_ID \
  --wait
```

**Download:**
```bash
notebooklm download report ./output/<slug>/report.md
```

**Options:**
- `--format`: briefing-doc (default), study-guide, blog-post, custom
- `--append`: Append extra instructions to built-in format prompt
- If description is provided without `--format`, auto-selects `custom`

---

## 4. Quiz

Generate multiple-choice quiz questions.

**Generate:**
```bash
notebooklm generate quiz [description] \
  --difficulty [easy|medium|hard] \
  --quantity [fewer|standard|more] \
  -s SOURCE_ID \
  --wait
```

**Download:**
```bash
notebooklm download quiz --format [json|markdown|html] ./output/<slug>/quiz.json
```

**Options:**
- `--difficulty`: easy, medium, hard
- `--quantity`: fewer, standard, more
- Download `--format`: json (default), markdown, html

---

## 5. Flashcards

Generate study flashcards.

**Generate:**
```bash
notebooklm generate flashcards [description] \
  --difficulty [easy|medium|hard] \
  --quantity [fewer|standard|more] \
  -s SOURCE_ID \
  --wait
```

**Download:**
```bash
notebooklm download flashcards --format [json|markdown|html] ./output/<slug>/flashcards.json
```

**Options:**
- `--difficulty`: easy, medium, hard
- `--quantity`: fewer, standard, more
- Download `--format`: json (default), markdown, html

---

## 6. Mind Map

Generate a hierarchical mind map. **This is the only synchronous artifact** — completes instantly, no `--wait` needed.

**Generate:**
```bash
notebooklm generate mind-map
```

**Download:**
```bash
notebooklm download mind-map ./output/<slug>/mindmap.json
```

**Notes:**
- Synchronous — returns immediately with result
- Output is a JSON tree structure
- No `--wait` option (not needed)

---

## 7. Slide Deck

Generate a presentation slide deck.

**Generate:**
```bash
notebooklm generate slide-deck [description] \
  --format [detailed|presenter] \
  --length [default|short] \
  -s SOURCE_ID \
  --wait
```

**Download:**
```bash
notebooklm download slide-deck --format [pdf|pptx] ./output/<slug>/slides.pdf
```

**Options:**
- Generate `--format`: detailed, presenter
- Generate `--length`: default, short
- Download `--format`: pdf (default), pptx

**Notes:**
- **Tier 2 artifact** — in agent mode, use `--json` instead of `--wait` for non-blocking generation. See "Deferred Generation" below.

**Post-generation (after `artifact wait` completes):**
Individual slides can be revised only after the initial generation completes:
```bash
notebooklm generate revise-slide "Move title up" --artifact <id> --slide 0 --wait
```

---

## 8. Infographic

Generate a visual infographic.

**Generate:**
```bash
notebooklm generate infographic [description] \
  --orientation [landscape|portrait|square] \
  --detail [concise|standard|detailed] \
  --style [auto|sketch-note|professional|bento-grid|editorial|instructional|bricks|clay|anime|kawaii|scientific] \
  -s SOURCE_ID \
  --wait
```

**Download:**
```bash
notebooklm download infographic ./output/<slug>/infographic.png
```

**Options:**
- `--orientation`: landscape, portrait, square
- `--detail`: concise, standard, detailed
- `--style`: 11 visual styles

---

## 9. Data Table

Generate a structured data table.

**Generate:**
```bash
notebooklm generate data-table <description> --wait
```

**Download:**
```bash
notebooklm download data-table ./output/<slug>/data.csv
```

**Notes:**
- Description is required (tells NotebookLM what to tabulate)
- Output is CSV with UTF-8 BOM for Excel compatibility

---

## Generation Order (recommended)

When generating multiple artifacts, use the two-tier strategy:

**Tier 1 — Generate with `--wait`** (deliver immediately):
1. **mind-map** — sync, instant
2. **report, quiz, flashcards, data-table** — 1-2 min each
3. **infographic** — 2-5 min

**Tier 2 — Generate with `--json`** (poll + deliver as completed):
4. **slide-deck** — 2-10 min
5. **video, audio** — 5-30 min

## Common Options (all generate commands)

- `-s/--source SOURCE_ID` — Select specific sources (repeatable; uses all if omitted)
- `--json` — Machine-readable output (returns `task_id` and `status`)
- `--language LANG` — Override output language
- `--retry N` — Auto-retry on rate limits with exponential backoff
- `--wait` — Block until generation completes (except mind-map which is always sync)

---

## Deferred Generation (Tier 2 Artifacts)

For slow artifacts (slide-deck, video, audio) that risk exceeding agent timeouts, use non-blocking generation with `--json` and poll for completion.

### Tier Classification

| Tier | Artifacts | Strategy | Max Time |
|------|-----------|----------|----------|
| **Tier 1 — Immediate** | mind-map, report, quiz, flashcards, data-table, infographic* | `--wait` (blocking) | < 5 min |
| **Tier 2 — Deferred** | slide-deck, video, audio | `--json` (non-blocking) → poll/wait | 5-30 min |

*\*infographic is borderline (2-5 min). If it times out in Tier 1, fall back to Tier 2 strategy on retry.*

### Step 1: Start Generation (non-blocking)

Use `--json` without `--wait` to start generation and get a `task_id`:

```bash
notebooklm generate slide-deck --format detailed --json
# → {"task_id": "abc123", "status": "pending"}

notebooklm generate video --style auto --json
# → {"task_id": "def456", "status": "pending"}

notebooklm generate audio "podcast instructions" --format deep-dive --json
# → {"task_id": "ghi789", "status": "pending"}
```

### Step 2: Wait for Completion

**`artifact wait`** — blocks until the artifact completes, fails, or times out. Use this in the skill workflow:
```bash
notebooklm artifact wait <task_id> --timeout 1800 --interval 5 --json
# Success → {"artifact_id": "<task_id>", "status": "completed", "url": "..."}
# Failure → {"artifact_id": "<task_id>", "error": "GENERATION_FAILED", "message": "..."}
# Timeout → {"artifact_id": "<task_id>", "status": "timeout", "error": "Timed out after 1800 seconds"}
```

**`artifact wait` options:**
- `--timeout SECONDS` — Max wait time (default: 300). Use 1800 for audio/video.
- `--interval SECONDS` — Initial poll interval (default: 2). Set to 5 for Tier 2 since these artifacts take minutes, not seconds. Uses exponential backoff internally.
- `--json` — Machine-readable output.

**Note on IDs:** The `task_id` returned by `generate --json` is the same value used as `artifact_id` in `artifact wait` responses. They are the same ID.

**`artifact poll`** — single status check, does NOT block. Use only for external monitoring or debugging, not in the skill workflow:
```bash
notebooklm artifact poll <task_id> --json
# → {"status": "processing"} | {"status": "completed"} | {"status": "failed"}
```

### Step 3: Download + Deliver

Once `artifact wait` returns `"status": "completed"`, download and deliver:

```bash
notebooklm download audio ./output/<slug>/podcast.mp3
bash scripts/compress_audio.sh ./output/<slug>/podcast.mp3 ./output/<slug>/podcast_compressed.mp3
# → deliver to Telegram
```

### Notes

- For media artifacts (audio, video, slide-deck, and infographic [Tier 1]), the API may report `completed` before media URLs are ready. The `artifact wait` command handles this internally by treating URL-less completions as still processing. This behavior applies to all media types regardless of tier.
- `artifact wait` uses exponential backoff — no need to implement custom retry logic.
- Process each Tier 2 artifact as it completes; don't wait for all before delivering.
- If `artifact wait` times out, notify the user and suggest downloading from NotebookLM directly.
