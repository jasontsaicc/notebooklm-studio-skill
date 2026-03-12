# Telegram Delivery Contract

## Goal
Ensure generated artifacts are delivered to Telegram with proper formatting and compatibility.

## Audio post-processing
After downloading audio, always run ffmpeg compression:

- Primary profile: mono, 24kHz, 64kbps MP3
- Fallback profile (if file > 45MB): mono, 22.05kHz, 48kbps MP3
- Telegram Bot API file size limit: 50MB

Reference script: `scripts/compress_audio.sh`

## Delivery types

### Text message (report summary + status table)
- `action`: send
- `channel`: telegram
- `target`: chat_id
- `text`: markdown-formatted summary

### File attachment (audio, video, quiz, flashcards, slides, infographic, data table, mind map)
- `action`: send
- `channel`: telegram
- `target`: chat_id
- `filePath`: local file path
- `caption`: short description

## Delivery order
1. Text summary (report + status table) — always first
2. Report (Markdown)
3. Quiz file (JSON/Markdown)
4. Flashcards file (JSON/Markdown)
5. Mind Map file (JSON)
6. Slides file (PDF/PPTX)
7. Infographic (PNG) — send as **photo** for better preview
8. Data Table (CSV)
9. Video (MP4)
10. Audio (MP3) — last, since it takes longest to generate

Only deliver artifacts that were requested and successfully generated.

## Special considerations

### Video
- Telegram 50MB file size limit applies
- No compression script available — if oversized, warn user and suggest downloading from NotebookLM directly
- Send as video (not document) for inline preview

### Infographic
- Send as **photo** (not document) for better Telegram preview
- If file is too large for photo upload, fallback to document

### Data Table
- Send as document with `.csv` extension
- Caption should note "UTF-8 CSV — opens in Excel/Google Sheets"

## Failure handling
- If compression fails, return `error_code=FFMPEG_COMPRESS_FAILED`.
- If upload fails, return `error_code=TELEGRAM_UPLOAD_FAILED`.
- Audio/Video failure must NOT block text artifact delivery.
- Report all failures in the status table with reason.
