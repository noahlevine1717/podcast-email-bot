# Podcast Knowledge Bot

A Telegram bot that transforms podcast episodes into professional summaries using Whisper transcription and Claude AI.

Send a podcast link, get back a structured summary with key points, notable quotes, and actionable takeaways. Refine with natural language feedback, save, and email.

## Features

- **Cloud or local transcription** - Groq (free, fast), OpenAI, or local faster-whisper
- **AI-powered summaries** - Professional format via Claude with key points, soundbites, takeaways
- **Natural language refinement** - "Make it shorter", "Focus on the AI discussion"
- **Learning system** - Improves summaries based on your feedback over time
- **Email integration** - Send summaries to your inbox (Resend or SMTP)
- **Access control** - Whitelist-based, only authorized Telegram users

## Deployment Options

### Option A: Railway (Recommended for 24/7 access)

1. Fork this repo on GitHub

2. Create a new project on [Railway](https://railway.app) and connect your fork

3. Add these environment variables in Railway:

   | Variable | Required | Description |
   |----------|----------|-------------|
   | `TELEGRAM_BOT_TOKEN` | Yes | From [@BotFather](https://t.me/botfather) |
   | `TELEGRAM_ALLOWED_USERS` | Yes | Your Telegram user ID (from [@userinfobot](https://t.me/userinfobot)) |
   | `ANTHROPIC_API_KEY` | Yes | From [console.anthropic.com](https://console.anthropic.com) |
   | `GROQ_API_KEY` | Yes | From [console.groq.com](https://console.groq.com) (free tier) |
   | `WHISPER_MODE` | No | `cloud` (default) or `local` |
   | `VAULT_PATH` | No | `/data/vault` (default) |
   | `RESEND_API_KEY` | No | For email features |
   | `EMAIL_ENABLED` | No | `true` to enable email |

4. Deploy - Railway auto-builds from the Dockerfile

> **Note:** If you set `OPENAI_API_KEY` with a Groq key (starts with `gsk_`), it will be detected as Groq automatically. This is for backward compatibility.

### Option B: Run Locally

1. **Prerequisites**: Python 3.11+, FFmpeg (`brew install ffmpeg`)

2. **Install**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/knowledge-bot.git
   cd knowledge-bot
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure** (pick one):
   ```bash
   # Option A: YAML config file
   cp config.yaml.example config.yaml
   # Edit config.yaml with your API keys

   # Option B: Environment variables
   cp .env.example .env
   # Edit .env with your API keys, then: source .env
   ```

4. **Run**:
   ```bash
   python -m src.bot
   ```

   To keep the bot running when you close the terminal:
   ```bash
   caffeinate -i python -m src.bot  # Prevents Mac sleep
   ```

## Getting Your Credentials

| Credential | Where to get it |
|------------|----------------|
| Telegram Bot Token | Message [@BotFather](https://t.me/botfather), send `/newbot` |
| Telegram User ID | Message [@userinfobot](https://t.me/userinfobot) |
| Anthropic API Key | [console.anthropic.com](https://console.anthropic.com) → API Keys |
| Groq API Key | [console.groq.com](https://console.groq.com) → API Keys (free) |

## Transcription Options

### Groq (Recommended)
Free tier, very fast transcription. 25MB file size limit (bot auto-compresses audio to fit).

```yaml
whisper:
  mode: "cloud"
  groq_api_key: "gsk_..."
```

### OpenAI Whisper API
Paid (~$0.006/min), no file size issues.

```yaml
whisper:
  mode: "cloud"
  openai_api_key: "sk-proj-..."
```

### Local (faster-whisper)
Free, private, requires decent CPU/GPU. Not available on Railway.

```yaml
whisper:
  mode: "local"
  model_size: "base"  # tiny, base, small, medium, large-v3
```

## Commands

| Command | Description |
|---------|-------------|
| `/podcast <url>` | Process a podcast episode |
| `/lookup` | Browse and manage saved summaries |
| `/status` | Check processing queue |
| `/stop` | Cancel stuck processes |
| `/stats` | View learning statistics |
| `/help` | Show available commands |
| `/poweron` / `/poweroff` | Start/stop bot (supervisor mode) |

### Supported Sources
- Spotify episode/show links
- Apple Podcasts links
- RSS feed URLs
- Direct audio URLs (MP3, M4A)

## Troubleshooting

### "Bot doesn't respond"
- Verify your Telegram user ID is in `allowed_users` (or `TELEGRAM_ALLOWED_USERS` env var)
- Check the bot token is correct
- On Railway: check deployment logs for errors

### "Groq transcription failed"
- **File too large**: The bot auto-compresses, but very long podcasts (3+ hours) may exceed Groq's 25MB limit. Try OpenAI instead.
- **Rate limited (429)**: Groq free tier has rate limits. Wait a minute and retry.
- **Trailing whitespace in key**: The bot auto-strips whitespace, but double-check your env var has no extra characters.

### "Can't find audio for Spotify podcast"
- Some Spotify podcasts are DRM-protected
- Try the podcast's RSS feed URL instead (search on podcasts.apple.com)
- If the wrong episode is matched, try a more specific Spotify episode link (not show link)

### "Telegram parse error in error messages"
- This is a known edge case with special characters in error text. The bot sanitizes output but some edge cases slip through. File an issue if you see this.

### "Bot is stuck / not responding to commands"
- Use `/stop` to clear all stuck sessions
- The ConversationHandler has a 10-minute timeout to auto-recover from stuck states

## Project Structure

```
knowledge-bot/
├── src/
│   ├── bot.py                # Main Telegram bot
│   ├── config.py             # Configuration (Pydantic models)
│   ├── processors/
│   │   └── podcast.py        # Audio download & transcription
│   ├── ai/
│   │   ├── summarizer.py     # Claude AI summaries
│   │   └── learning.py       # Preference learning
│   └── storage/
│       └── summaries.py      # JSON-based persistence
├── Dockerfile                # Cloud deployment (Railway)
├── railway.toml              # Railway config
├── requirements.txt          # Full local dependencies
├── requirements-cloud.txt    # Cloud-only dependencies (no PyTorch)
├── config.yaml.example       # Configuration template (YAML)
├── .env.example              # Configuration template (env vars)
└── README.md
```

## Security

- **Access control**: Only whitelisted Telegram user IDs can use the bot
- **Secrets**: All API keys in `config.yaml` (gitignored) or environment variables
- **SSRF protection**: URL validation before fetching audio
- **Error sanitization**: No internal paths/stack traces in user-facing messages
- Never commit `config.yaml` or `.env` files

## License

MIT
