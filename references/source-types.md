# Supported Source Types

## Source type mapping

| Type     | Telegram input            | notebooklm-py method      | Notes                      |
|----------|--------------------------|---------------------------|----------------------------|
| url      | Paste article link       | `sources.add_url()`       | Any web article URL        |
| youtube  | Paste YouTube link       | `sources.add_url()`       | YouTube video URL          |
| text     | Type or paste text       | `sources.add_text()`      | Raw text / notes           |
| pdf      | Upload .pdf file         | `sources.add_file()`      | PDF document               |
| word     | Upload .docx file        | `sources.add_file()`      | Word document              |
| audio    | Upload audio file        | `sources.add_file()`      | Audio recording            |
| image    | Upload image file        | `sources.add_file()`      | Image with text content    |
| drive    | Paste Google Drive link  | `sources.add_drive()`     | Google Drive shared file   |

## Auto-detection rules

When the user sends content via Telegram, detect the source type:

1. **URL pattern** (`https?://...`):
   - Contains `youtube.com` or `youtu.be` → type: `youtube`
   - Contains `drive.google.com` or `docs.google.com` → type: `drive`
   - Otherwise → type: `url`
2. **File attachment**:
   - `.pdf` extension → type: `pdf`
   - `.docx` / `.doc` extension → type: `word`
   - `.mp3` / `.wav` / `.m4a` / `.ogg` extension → type: `audio`
   - `.jpg` / `.jpeg` / `.png` / `.webp` extension → type: `image`
3. **Plain text** (no URL, no file) → type: `text`

## sources.json format

```json
[
  {"type": "url", "content": "https://example.com/article"},
  {"type": "youtube", "content": "https://youtube.com/watch?v=xxx"},
  {"type": "text", "content": "My learning notes about..."},
  {"type": "pdf", "content": "/path/to/document.pdf"},
  {"type": "drive", "content": "https://drive.google.com/file/d/xxx"}
]
```
