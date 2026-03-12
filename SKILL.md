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

6. **Generate artifacts** — In speed order (fast first):
   ```bash
   # Sync (instant)
   notebooklm generate mind-map

   # Fast async (1-2 min)
   notebooklm generate report --format study-guide --wait
   notebooklm generate quiz --difficulty medium --wait
   notebooklm generate flashcards --wait
   notebooklm generate data-table "describe table structure" --wait

   # Medium async (2-10 min)
   notebooklm generate infographic --orientation landscape --wait
   notebooklm generate slide-deck --format detailed --wait

   # Slow async (5-30 min) — warn user about wait time
   notebooklm generate video --style auto --wait
   notebooklm generate audio "custom instructions" --format deep-dive --wait
   ```
   Only generate the artifacts the user requested. Skip the rest.

7. **Download** — Each successful artifact into `./output/<slug>/`:
   ```bash
   notebooklm download mind-map ./output/<slug>/mindmap.json
   notebooklm download report ./output/<slug>/report.md
   notebooklm download quiz --format json ./output/<slug>/quiz.json
   notebooklm download flashcards --format json ./output/<slug>/flashcards.json
   notebooklm download data-table ./output/<slug>/data.csv
   notebooklm download infographic ./output/<slug>/infographic.png
   notebooklm download slide-deck ./output/<slug>/slides.pdf
   notebooklm download video ./output/<slug>/video.mp4
   notebooklm download audio ./output/<slug>/podcast.mp3
   ```

8. **Post-process** — If audio was generated, compress for file size:
   ```bash
   bash scripts/compress_audio.sh ./output/<slug>/podcast.mp3 ./output/<slug>/podcast_compressed.mp3
   ```

9. **Report results** — Present artifact status and file paths to user.

10. **Deliver to Telegram** (OpenClaw only) — If `message` tool is available:
   1. Text summary (always first)
   2. Report → Quiz → Flashcards → Mind Map → Slides → Infographic → Data Table → Video → Audio

   See `references/telegram-delivery.md` for delivery contract.
   Skip this step if running outside OpenClaw (e.g. Claude Code, Codex).

## Error handling

- Retry up to **2 times** on transient errors (rate limits, timeouts).
- **Auth errors** → stop immediately, report to user.
- **Audio/Video failure must NOT block** text artifact delivery.
- Capture failure reason in delivery status.

Fallback order:
1. Deliver all completed text artifacts on time.
2. Append failure notes for any failed artifacts with reason.
3. Suggest retry window for failed long-running artifacts.

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
