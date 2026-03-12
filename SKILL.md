---
name: notebooklm-studio
description: >
  Import sources (URLs, YouTube, files, text) into Google NotebookLM
  and generate user-selected artifacts: podcast, video, report, quiz,
  flashcards, mind map, slides, infographic, data table.
  Use when the user sends content and asks to generate learning
  materials, podcasts, videos, or study packages.
version: 2.0.0
metadata:
  openclaw:
    requires:
      bins: [notebooklm, ffmpeg]
    emoji: "🎙️"
---

# NotebookLM Studio

Import sources into NotebookLM, generate user-selected artifacts via CLI, download results locally.

## Inputs

Collect from user message (ask only for missing fields):

- **Sources**: URLs, YouTube links, text notes, or file attachments (PDF, Word, audio, image, Google Drive link)
- **Artifacts**: User selects from 9 types (no default — always ask):
  - `audio` (podcast), `video`, `report`, `quiz`, `flashcards`, `mind-map`, `slide-deck`, `infographic`, `data-table`
- **Language** (optional, default: `zh_Hant`): applied via `notebooklm language set`
  - ⚠️ This is a **GLOBAL** setting — affects all notebooks in the account
- **Custom instructions** (optional): passed as description to generate commands
- **Telegram target** (optional, OpenClaw only): chat_id for delivery

See `references/source-types.md` for source type detection rules.
See `references/artifacts.md` for all 9 artifact types and CLI options.

## Workflow

1. **Parse input** — Detect source types from user message (URLs, files, text). Confirm which artifacts to generate.

2. **Derive slug** — Based on the sources and user message, generate a short kebab-case slug (2-4 words) that captures the core topic. This slug is used for both the notebook name and the output directory.
   - Examples: `react-server-components`, `feynman-technique`, `taiwan-semiconductor-q4`
   - Keep it concise, lowercase, ASCII-only (transliterate non-ASCII if needed)
   - If the user provides a topic or title, prefer that as the basis

3. **Create notebook** —
   ```bash
   notebooklm create "<slug> <YYYYMMDD>"
   notebooklm use <notebook_id>
   mkdir -p ./output/<slug>
   ```

4. **Set language** —
   ```bash
   notebooklm language set zh_Hant
   ```
   ⚠️ GLOBAL setting — always set explicitly to avoid residual from previous runs.

5. **Add sources** — For each source:
   ```bash
   # URL, YouTube, or file path
   notebooklm source add "<url_or_filepath>"

   # Google Drive
   notebooklm source add-drive <file_id> "<title>"
   ```
   For plain text → save to a `.txt` file first, then `source add "./temp_text.txt"`.

6. **Generate artifacts** — Two-tier strategy for timeout safety:

   **Tier 1 — Immediate** (use `--wait`, completes within timeout):
   ```bash
   # Sync (instant)
   notebooklm generate mind-map

   # Fast async (1-2 min)
   notebooklm generate report --format study-guide --wait
   notebooklm generate quiz --difficulty medium --wait
   notebooklm generate flashcards --wait
   notebooklm generate data-table "describe table structure" --wait

   # Medium async (2-5 min, borderline — if timeout, retry or move to Tier 2)
   notebooklm generate infographic --orientation landscape --wait
   ```

   **Tier 2 — Deferred** (use `--json` without `--wait`, capture `task_id` for step 9):
   ```bash
   # Slow async — parse JSON output to extract task_id for polling
   notebooklm generate slide-deck --format detailed --json
   # → {"task_id": "abc123", "status": "pending"}  ← save task_id

   notebooklm generate video --style auto --json
   # → {"task_id": "def456", "status": "pending"}  ← save task_id

   notebooklm generate audio "custom instructions" --format deep-dive --json
   # → {"task_id": "ghi789", "status": "pending"}  ← save task_id
   ```
   Parse each JSON response and save the `task_id` — you will need it in step 9.
   Only generate the artifacts the user requested. Skip the rest.
   See `references/artifacts.md` → "Deferred Generation" for Tier 2 details.

7. **Download Tier 1** — Each successful Tier 1 artifact into `./output/<slug>/`:
   ```bash
   notebooklm download mind-map ./output/<slug>/mindmap.json
   notebooklm download report ./output/<slug>/report.md
   notebooklm download quiz --format json ./output/<slug>/quiz.json
   notebooklm download flashcards --format json ./output/<slug>/flashcards.json
   notebooklm download data-table ./output/<slug>/data.csv
   notebooklm download infographic ./output/<slug>/infographic.png
   ```

8. **Report + Deliver Tier 1** — Present completed Tier 1 artifacts to user.
   If Tier 2 artifacts are pending, include a status note:
   > "Slides/Audio/Video are still generating, I'll send them when ready."

   **Telegram delivery** (OpenClaw only) — If `message` tool is available:
   1. Text summary with Tier 2 pending status (always first)
   2. Report → Quiz → Flashcards → Mind Map → Infographic → Data Table

   See `references/telegram-delivery.md` for delivery contract.
   Skip Telegram delivery if running outside OpenClaw (e.g. Claude Code, Codex).

9. **Poll + Deliver Tier 2** — Wait for each deferred artifact in order of expected speed (fastest first), then download and deliver as each completes:
   ```bash
   # Wait by expected completion order: slide-deck (fastest) → video → audio (slowest)
   # Uses --interval 5 (not default 2) since Tier 2 artifacts take minutes, not seconds
   notebooklm artifact wait <slide_task_id> --timeout 1800 --interval 5 --json
   # → {"status": "completed", ...}  ← task_id from generate is used as artifact_id here
   notebooklm download slide-deck ./output/<slug>/slides.pdf
   # → deliver to Telegram immediately

   notebooklm artifact wait <video_task_id> --timeout 1800 --interval 5 --json
   notebooklm download video ./output/<slug>/video.mp4
   # → deliver to Telegram immediately

   notebooklm artifact wait <audio_task_id> --timeout 1800 --interval 5 --json
   notebooklm download audio ./output/<slug>/podcast.mp3
   bash scripts/compress_audio.sh ./output/<slug>/podcast.mp3 ./output/<slug>/podcast_compressed.mp3
   # → deliver to Telegram immediately
   ```
   - **Order matters**: wait for fastest artifact first (slide-deck → video → audio) to minimize idle time
   - On completion: download → post-process → deliver to Telegram immediately
   - On failure: notify user with error reason, continue to next artifact
   - On timeout: notify user, suggest downloading from NotebookLM directly
   - Max wait: 30 minutes per artifact (covers worst-case audio/video)

## Error handling

- **Auth errors** → stop immediately, report to user.
- **Tier 1 failure**: retry up to 2 times, then include failure note in step 8 delivery.
- **Tier 2 failure**: notify user per-artifact in step 9. Tier 1 is already delivered by this point, so Tier 2 failures never block text artifact delivery.
- Capture failure reason in delivery status.

## Quality gate

Before delivery, verify:
- Sources are concrete article/content pages (not category/index pages).
- Report contains actionable takeaways (not generic summary).
- Quiz tests key concepts and mechanics.
- Flashcards focus on terms, decisions, and trade-offs.
- Output respects requested language and length.

See `references/output-contracts.md` for format specifications.

## Delivery template

1. Selection rationale (<=3 bullets)
2. Artifact list with paths/status (all 9 types if applicable)
3. Key takeaways (3-5 bullets)
4. Failures + fallback note (if any)
5. One discussion question
