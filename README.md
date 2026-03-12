# NotebookLM Studio Skill

AI agent skill for Google NotebookLM — import sources (URLs, YouTube, files, text) and generate podcasts, videos, reports, quizzes, flashcards, mind maps, slides, infographics, and data tables.

Works with **Claude Code**, **OpenClaw**, **Codex**, and any agent that supports the [Agent Skills](https://agentskills.io) specification.

## Features

- **9 artifact types**: audio, video, report, quiz, flashcards, mind-map, slide-deck, infographic, data-table
- **No default mode**: user selects which artifacts to generate
- **All source types**: URLs, YouTube, text notes, PDF, Word, audio, images, Google Drive
- **Cross-platform**: works with any AI agent that reads SKILL.md
- **Telegram delivery**: optional, via OpenClaw `message` tool
- **Audio compression**: ffmpeg post-processing for large file handling
- **CLI-driven**: uses `notebooklm` CLI directly — no custom Python wrappers

## Setup

### 1. Clone with submodule

```bash
git clone --recurse-submodules https://github.com/<your-org>/notebooklm-studio-skill.git
# Or if already cloned:
git submodule update --init
```

### 2. Install notebooklm-py

```bash
cd notebooklm-py && pip install -e ".[browser]" && cd ..
playwright install chromium
```

### 3. Authenticate

```bash
notebooklm login
```

This opens a browser for Google account login. On remote servers, run login locally and transfer `storage_state.json`:

```bash
scp ~/.notebooklm/storage_state.json user@server:~/.notebooklm/storage_state.json
chmod 600 ~/.notebooklm/storage_state.json
```

### 4. Verify

```bash
notebooklm auth check --test
```

### 5. Install as agent skill

**Claude Code:**
```bash
ln -s /path/to/notebooklm-studio-skill ~/.claude/skills/notebooklm-studio
```

**OpenClaw:**
```bash
ln -s /path/to/notebooklm-studio-skill /path/to/openclaw/skills/notebooklm-studio
```

**Other agents:** Place or symlink the directory where your agent discovers skills.

## Architecture

```
User (Telegram / CLI / IDE)
    │
    ▼
AI Agent (Claude Code / OpenClaw / Codex)
    │  reads SKILL.md workflow
    ▼
notebooklm CLI (via notebooklm-py submodule)
    ├── notebooklm create / use
    ├── notebooklm source add
    ├── notebooklm generate <type> --wait
    └── notebooklm download <type>
    │
    ▼
./output/ (local artifacts)
    │
    ▼ (optional, OpenClaw only)
Telegram delivery via message tool
```

## Artifact Types

| Type | CLI Command | Est. Time | Output |
|------|-------------|-----------|--------|
| Audio (Podcast) | `generate audio` | 5-30 min | MP3 |
| Video | `generate video` | 5-30 min | MP4 |
| Report | `generate report` | 1-2 min | Markdown |
| Quiz | `generate quiz` | 1-2 min | JSON/MD/HTML |
| Flashcards | `generate flashcards` | 1-2 min | JSON/MD/HTML |
| Mind Map | `generate mind-map` | Instant | JSON |
| Slide Deck | `generate slide-deck` | 2-10 min | PDF/PPTX |
| Infographic | `generate infographic` | 2-5 min | PNG |
| Data Table | `generate data-table` | 1-2 min | CSV |

See `references/artifacts.md` for full CLI options.

## Repository Structure

```
notebooklm-studio-skill/
├── .gitmodules                      # git submodule config
├── .gitignore
├── SKILL.md                         # Agent skill definition (CLI workflow)
├── README.md
├── LICENSE
├── notebooklm-py/                   # git submodule (notebooklm CLI)
├── references/
│   ├── artifacts.md                 # 9 artifact types reference
│   ├── source-types.md              # Source types & detection rules
│   ├── output-contracts.md          # Output format specifications
│   └── telegram-delivery.md         # Telegram delivery contract (OpenClaw)
└── scripts/
    └── compress_audio.sh            # ffmpeg audio compression
```

## Updating notebooklm-py

```bash
cd notebooklm-py && git pull origin main && cd ..
pip install -e "notebooklm-py[browser]"
```

## Powered By

- [notebooklm-py](https://github.com/teng-lin/notebooklm-py) — Unofficial Python API & CLI for Google NotebookLM

## License

MIT
