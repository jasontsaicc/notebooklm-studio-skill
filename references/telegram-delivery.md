# Telegram Delivery Contract

## Goal
Ensure generated audio is upload-ready for Telegram with predictable size and compatibility.

## Post-processing
After `generate_audio`, always run ffmpeg compression:

- Primary profile: mono, 24kHz, 64kbps MP3
- Fallback profile (if still large): mono, 22.05kHz, 48kbps MP3

Reference script:
- `scripts/compress_audio.sh`

## Delivery fields
- `audio.raw_artifact`: original path/url
- `audio.compressed_artifact`: compressed MP3 path/url
- `audio.compression_profile`: `64k_24k_mono` or `48k_22k_mono`
- `audio.delivery_target`: e.g. `telegram:-5117247168`

## Failure handling
- If compression fails, return `error_code=FFMPEG_COMPRESS_FAILED`.
- If upload fails, return `error_code=TELEGRAM_UPLOAD_FAILED`.
- Do not drop text artifacts because of audio delivery failure.
