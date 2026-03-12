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
notebooklm download audio ./output/podcast.mp3
```

**Options:**
- `--format`: deep-dive (default), brief, critique, debate
- `--length`: short, default, long
- `--language`: Language code (default: en)
- `-s/--source`: Select specific sources (repeatable)

**Notes:**
- Longest generation time (5-30 min)
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
notebooklm download video ./output/video.mp4
```

**Options:**
- `--format`: explainer, brief, cinematic
- `--style`: 9 visual styles (auto, classic, whiteboard, kawaii, anime, watercolor, retro-print, heritage, paper-craft)
- `--language`: Language code

**Notes:**
- Generation time similar to audio (5-30 min)
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
notebooklm download report ./output/report.md
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
notebooklm download quiz --format [json|markdown|html] ./output/quiz.json
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
notebooklm download flashcards --format [json|markdown|html] ./output/flashcards.json
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
notebooklm download mind-map ./output/mindmap.json
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
notebooklm download slide-deck --format [pdf|pptx] ./output/slides.pdf
```

**Options:**
- Generate `--format`: detailed, presenter
- Generate `--length`: default, short
- Download `--format`: pdf (default), pptx

**Post-generation:**
Individual slides can be revised:
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
notebooklm download infographic ./output/infographic.png
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
notebooklm download data-table ./output/data.csv
```

**Notes:**
- Description is required (tells NotebookLM what to tabulate)
- Output is CSV with UTF-8 BOM for Excel compatibility

---

## Generation Order (recommended)

When generating multiple artifacts, order by speed for fastest user delivery:

1. **mind-map** — sync, instant
2. **report, quiz, flashcards, data-table** — 1-2 min each, use `--wait`
3. **infographic, slide-deck** — 2-10 min, use `--wait`
4. **video, audio** — 5-30 min, use `--wait`, warn user about wait time

## Common Options (all generate commands)

- `-s/--source SOURCE_ID` — Select specific sources (repeatable; uses all if omitted)
- `--json` — Machine-readable output (returns `task_id` and `status`)
- `--language LANG` — Override output language
- `--retry N` — Auto-retry on rate limits with exponential backoff
- `--wait` — Block until generation completes (except mind-map which is always sync)
