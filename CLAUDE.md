# Podcast Knowledge Bot - Developer Documentation

## Product Overview

A Telegram bot that transforms podcast episodes into structured, email-ready summaries using Whisper transcription and Claude AI. Supports natural language refinement and learns from user feedback.

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  Telegram Bot   │────▶│   Processing Layer   │────▶│  JSON Storage   │
│  (Interface)    │     │                      │     │  (Summaries)    │
└─────────────────┘     │  - yt-dlp            │     └─────────────────┘
                        │  - feedparser        │              │
                        │  - ffmpeg (compress) │              │
                        └──────────────────────┘              ▼
                                    │                 ┌─────────────────┐
                                    ▼                 │   AI Layer      │
                        ┌──────────────────────┐      │  (Claude API)   │
                        │  Transcription       │      │  - Summaries    │
                        │  - Groq (cloud)      │      │  - Refinement   │
                        │  - OpenAI (cloud)    │      └─────────────────┘
                        │  - faster-whisper    │              │
                        └──────────────────────┘              ▼
                                                      ┌─────────────────┐
                                                      │ Learning System │
                                                      │ (Preferences)   │
                                                      └─────────────────┘
```

### Tech Stack
- **Language**: Python 3.11+
- **Bot Framework**: python-telegram-bot (async)
- **Transcription**: Groq Whisper API (cloud, free), OpenAI Whisper API, or faster-whisper (local)
- **Audio Extraction**: yt-dlp, feedparser, ffmpeg
- **AI**: Claude API via Anthropic SDK
- **Email**: Resend API (or SMTP)
- **Config**: Pydantic models with YAML + env var loading
- **Deployment**: Docker on Railway

---

## Key Files

| File | Purpose |
|------|---------|
| `src/bot.py` | Main Telegram bot - handlers, conversation flows, email sending |
| `src/config.py` | Pydantic configuration models, env var loading, Groq key detection |
| `src/ai/summarizer.py` | Claude API integration for generating/refining summaries |
| `src/ai/learning.py` | Feedback tracking and preference learning system |
| `src/processors/podcast.py` | Audio extraction (yt-dlp), compression (ffmpeg), Whisper transcription |
| `src/storage/summaries.py` | JSON-based summary persistence |
| `Dockerfile` | Cloud build - python:3.11-slim + ffmpeg, uses requirements-cloud.txt |
| `railway.toml` | Railway deploy config (dockerfile builder, restart on failure) |
| `requirements.txt` | Full local deps (includes faster-whisper, sentence-transformers) |
| `requirements-cloud.txt` | Cloud deps (no PyTorch/faster-whisper for smaller image) |
| `.env.example` | Env var template for local dev or Railway |
| `config.yaml` | User configuration (gitignored - contains secrets) |
| `config.yaml.example` | YAML config template |

---

## Railway Deployment

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from @BotFather |
| `TELEGRAM_ALLOWED_USERS` | Yes | Comma-separated Telegram user IDs |
| `ANTHROPIC_API_KEY` | Yes | Claude API key |
| `GROQ_API_KEY` | Yes | Groq API key (or use `OPENAI_API_KEY` with gsk_ prefix) |
| `OPENAI_WHISPER_KEY` | No | Real OpenAI key for automatic fallback on Groq 429/413 |
| `WHISPER_MODE` | No | `cloud` (default) or `local` |
| `VAULT_PATH` | No | Data storage path (default: `/data/vault`) |
| `AI_MODEL` | No | Claude model (default: `claude-sonnet-4-20250514`) |
| `RESEND_API_KEY` | No | For email features |
| `EMAIL_ENABLED` | No | `true`/`false` |
| `DIGEST_TIME` | No | Daily digest time (default: `20:00`) |
| `DIGEST_TIMEZONE` | No | Timezone (default: `America/Los_Angeles`) |

### Groq Key Detection Logic (`src/config.py`)
The `_get_groq_key()` function checks:
1. `GROQ_API_KEY` env var (primary, documented)
2. `OPENAI_API_KEY` starting with `gsk_` (backward compat for Railway)

This means on Railway you can set either `GROQ_API_KEY=gsk_...` or `OPENAI_API_KEY=gsk_...` and Groq will be detected.

---

## Bot Modes

### AI-Only Mode
1. User sends `/podcast <url>`
2. Bot transcribes and generates summary automatically
3. User reviews and can approve or provide feedback
4. Summary saved to storage

### Interactive "Highlighting" Mode
1. User sends `/podcast <url>` and selects interactive mode
2. While listening, user adds highlights:
   - `/detail <text>` - Key facts, stats, points
   - `/insight <text>` - Personal takeaways, connections
3. User sends `/end` when done
4. AI generates summary incorporating user's highlights
5. Review, refine, save

---

## Common Bugs / Known Issues

### ConversationHandler Stuck State
**Problem**: When callbacks are triggered from background tasks (`asyncio.create_task`), the ConversationHandler may not catch them, leaving the user stuck.
**Solution**: A standalone `CallbackQueryHandler` is registered outside the ConversationHandler (line ~1816 in bot.py). The ConversationHandler also has a `conversation_timeout=600` (10 minutes) to auto-recover.

### Groq 25MB File Limit
**Problem**: Groq's Whisper API rejects files over 25MB.
**Solution**: The podcast processor auto-compresses audio with ffmpeg before sending. Very long podcasts (3+ hours) may still exceed the limit after compression.

### Trailing Whitespace in API Keys
**Problem**: Copy-pasting API keys from web UIs sometimes includes trailing newlines or spaces, causing auth failures.
**Solution**: All env var reads in `config.py` call `.strip()` on the value.

### 429 Rate Limit on Groq Free Tier
**Problem**: Groq's free tier has per-hour audio limits (~2 hours/hour). Back-to-back podcast processing can hit this.
**Solution**: If `OPENAI_WHISPER_KEY` is set, the bot automatically falls back to OpenAI and notifies the user. Without it, the error surfaces and user must wait ~20 min.

### Telegram Markdown Parse Errors
**Problem**: Special characters in error messages or summaries can cause `telegram.error.BadRequest` when using MarkdownV2 parse mode.
**Solution**: The bot sanitizes output, but edge cases with nested formatting can slip through. Error messages are sent as plain text.

### Spotify Episode Matching (Wrong Episode)
**Problem**: When given a Spotify show link (not episode), yt-dlp may match the wrong episode.
**Solution**: Users should provide specific episode links. The bot extracts episode metadata from Spotify's page when possible.

---

## Learning System

Tracks user preferences to improve summaries over time:
- **Length**: brief / medium / detailed
- **Detail level**: high-level / balanced / granular
- **Tone**: casual / professional / academic
- **Features**: timestamps, soundbites, takeaways
- **Feedback patterns**: Common phrases the user uses

Preferences stored in `data/learning.json`, injected into summarizer prompts.

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Show available commands |
| `/podcast <url>` | Process a podcast |
| `/lookup` | Browse saved summaries |
| `/status` | Check processing queue and active sessions |
| `/stop` | Cancel all stuck processes and clear session state |
| `/stats` | View learning statistics |
| `/poweron` / `/poweroff` | Start/stop bot (supervisor mode) |
| `/cancel` | Cancel current operation |

### Interactive Mode Commands
| Command | Description |
|---------|-------------|
| `/detail <text>` | Add a key fact or point |
| `/insight <text>` | Add a personal takeaway |
| `/end` | Generate summary with highlights |

---

## Security

- **Access control**: `allowed_users` whitelist in config
- **SSRF protection**: URL validation before fetching
- **Error sanitization**: No internal paths/details in user-facing errors
- **Secrets management**: All keys in gitignored config.yaml or env vars
- **No secrets in source**: `_get_groq_key()` reads from env only

---

## Development

### Running Locally
```bash
source .venv/bin/activate
python -m src.bot
```

### Adding New Content Types
1. Create processor in `src/processors/`
2. Add handler in `src/bot.py`
3. Update summarizer prompt if needed

### Modifying Summary Format
Edit the prompt in `src/ai/summarizer.py`. The learning system injects user preferences automatically.

### Testing Transcription
```python
from src.processors.podcast import PodcastProcessor
processor = PodcastProcessor(config)
transcript = await processor.transcribe("path/to/audio.mp3")
```
