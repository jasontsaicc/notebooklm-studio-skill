# Telegram Delivery Contract

## Goal
Ensure generated artifacts are delivered to Telegram with proper formatting and compatibility.

## Audio post-processing
After `generate_audio`, always run ffmpeg compression:

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

### File attachment (audio, quiz JSON, flashcards JSON, slides)
- `action`: send
- `channel`: telegram
- `target`: chat_id
- `filePath`: local file path
- `caption`: short description

## Delivery fields
- `audio.raw_artifact`: original path/url
- `audio.compressed_artifact`: compressed MP3 path/url
- `audio.compression_profile`: `64k_24k_mono` or `48k_22k_mono`
- `delivery_target`: e.g. `telegram:-5117247168`

## Delivery order
1. Text summary (report + status table) — always first
2. Quiz JSON file (if generated)
3. Flashcards JSON file (if generated)
4. Mind map JSON file (if generated)
5. Slides file (if generated)
6. Audio file (last, since it takes longest to generate)

## Failure handling
- If compression fails, return `error_code=FFMPEG_COMPRESS_FAILED`.
- If upload fails, return `error_code=TELEGRAM_UPLOAD_FAILED`.
- Do not drop text artifacts because of audio delivery failure.
