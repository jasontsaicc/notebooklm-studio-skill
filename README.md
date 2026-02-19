# OpenClaw NotebookLM Studio Skill

Upload articles, notes, or files from Telegram via OpenClaw Bot to Google NotebookLM — automatically generate podcasts, reports, quizzes, flashcards, mind maps, and slides, then deliver results back to Telegram.

## Features

- **6 output modes**: podcast-only, report-only, study-pack, full-pack, explore-pack, all-in-one
- **All source types**: URLs, YouTube, text notes, PDF, Word, audio, images, Google Drive
- **Telegram integration**: Send content → get results back in the same chat
- **Reliability**: Auto-retry, timeout handling, graceful degradation (text artifacts always delivered)
- **Audio compression**: ffmpeg post-processing for Telegram-friendly file sizes
- **Multi-language**: Default zh-Hant for text, en for podcasts (configurable)

## Repository Structure

```
openclaw-notebooklm-studio-skill/
├── SKILL.md                        # OpenClaw Skill definition
├── requirements.txt                # Python dependencies
├── scripts/
│   ├── adapter_interface.py        # Abstract adapter interface
│   ├── notebooklm_adapter.py       # notebooklm-py adapter (all artifact types)
│   ├── run_pipeline.py             # Main pipeline orchestrator
│   ├── compress_audio.sh           # ffmpeg audio compression
│   └── build_delivery_payload.py   # Telegram delivery payload builder
├── references/
│   ├── modes.md                    # Output mode definitions
│   ├── output-contracts.md         # Artifact format specifications
│   ├── source-types.md             # Supported source types & detection rules
│   ├── telegram-delivery.md        # Telegram delivery contract
│   └── auth-setup.md               # Authentication & setup guide
└── examples/
    ├── devops-input.json           # Example: DevOps sources
    ├── system-design-input.json    # Example: System Design sources
    ├── payload-sample.json         # Example: delivery payload
    └── smoke-test-output.json      # Example: smoke test output
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt

# First-time setup (browser login)
pip install "notebooklm-py[browser]"
playwright install chromium
```

### 2. Authenticate NotebookLM

```bash
notebooklm login
```

See [references/auth-setup.md](references/auth-setup.md) for remote server setup.

### 3. Verify setup

```bash
cd scripts/
python notebooklm_adapter.py --smoke-test
```

### 4. Add to OpenClaw workspace

Copy or symlink this skill into your OpenClaw skills directory:

```bash
ln -s /path/to/openclaw-notebooklm-studio-skill /path/to/openclaw/skills/notebooklm-studio
```

## Usage

### Via OpenClaw Bot (Telegram)

Send content to the bot in Telegram:

```
Here are some articles about Kubernetes:
https://example.com/k8s-best-practices
https://example.com/k8s-security-guide

Generate a full-pack please.
```

The bot will:
1. Detect source types (URLs)
2. Create a NotebookLM notebook
3. Import sources
4. Generate report, quiz, flashcards, and podcast
5. Deliver results back to Telegram

### Direct CLI Usage

```bash
# Prepare sources file
cat > sources.json << 'EOF'
[
  {"type": "url", "content": "https://example.com/article"},
  {"type": "text", "content": "My notes about the topic..."}
]
EOF

# Run pipeline
python scripts/run_pipeline.py \
  --mode full-pack \
  --sources-file sources.json \
  --notebook-title "My Study Session" \
  --language zh-Hant \
  --output-dir ./output

# Build delivery payload
python scripts/build_delivery_payload.py \
  --pipeline-result output/result.json \
  --target telegram:-5117247168 \
  --payload-out output/delivery.json
```

## Output Modes

| Mode | Artifacts | Best For |
|------|-----------|----------|
| `podcast-only` | Audio (MP3) | Commute listening |
| `report-only` | Markdown report | Quick reading |
| `study-pack` | Report + Quiz + Flashcards | Deep learning |
| `full-pack` | Study-pack + Audio | Daily content package |
| `explore-pack` | Report + Mind Map + Slides | Topic exploration |
| `all-in-one` | Everything | Complete experience |

## Architecture

```
Telegram User
    │
    ▼
OpenClaw Bot (receives message)
    │
    ▼
SKILL.md (AI Agent reads workflow)
    │
    ▼
run_pipeline.py (orchestrator)
    ├── notebooklm_adapter.py → NotebookLM API (via notebooklm-py)
    │   ├── Create notebook
    │   ├── Import sources (URL/text/file/Drive)
    │   └── Generate artifacts (audio/report/quiz/flashcards/mindmap/slides)
    └── compress_audio.sh → ffmpeg (audio post-processing)
    │
    ▼
build_delivery_payload.py
    │
    ▼
OpenClaw message tool → Telegram
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `NLM_STORAGE_PATH` | (auto) | Path to storage_state.json |
| `NLM_OUTPUT_DIR` | `/tmp/notebooklm-output` | Output directory |
| `NLM_TIMEOUT_SECONDS` | `1200` | Audio generation timeout |

## Powered By

- [notebooklm-py](https://github.com/teng-lin/notebooklm-py) — Unofficial Python API for Google NotebookLM
- [OpenClaw](https://openclaw.ai) — AI agent platform

## License

MIT
