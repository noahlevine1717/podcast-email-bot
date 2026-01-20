# Podcast Knowledge Bot

A Telegram bot that transforms podcast episodes into professional email-style summaries using Whisper transcription (local or cloud) and Claude AI.

## What It Does

1. **Send a podcast link** (Spotify, Apple Podcasts, or RSS feed URL)
2. **Bot transcribes** the audio using Whisper (local or OpenAI cloud API)
3. **Claude AI generates** a professional email-style summary with:
   - Key discussion points
   - Notable soundbites with timestamps
   - Actionable takeaways
4. **Review and refine** the summary with natural language feedback
5. **Save, email, or edit** your summaries anytime

## Features

- **Flexible transcription** - Choose local (free, private) or cloud (fast, ~$0.006/min)
- **AI-powered summaries** - Professional, email-ready format via Claude
- **Interactive editing** - Refine summaries with natural language feedback
- **Persistent storage** - All summaries saved and searchable via Telegram
- **Email integration** - Send summaries directly to your inbox
- **Secure** - Restricted to authorized Telegram users only

## Quick Start

### Prerequisites

- Python 3.11+
- A Telegram account
- An Anthropic API key ([get one here](https://console.anthropic.com))
- FFmpeg installed (`brew install ffmpeg` on macOS)
- **For cloud transcription:** OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd podcast-email-bot
   ```

2. **Create virtual environment and install**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

3. **Create your configuration**:
   ```bash
   cp config.yaml.example config.yaml
   ```

4. **Edit `config.yaml`** with your credentials (see Configuration section below)

5. **Run the bot**:
   ```bash
   python -m src.bot
   ```

## Configuration

Edit `config.yaml` with your settings:

### Required Settings

```yaml
telegram:
  bot_token: "YOUR_TELEGRAM_BOT_TOKEN"
  allowed_users: [YOUR_TELEGRAM_USER_ID]  # Security: restrict access

ai:
  anthropic_api_key: "YOUR_ANTHROPIC_API_KEY"
```

### Getting Your Credentials

#### Telegram Bot Token
1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the prompts
3. Copy the token (looks like `123456789:ABCdefGHI...`)

#### Your Telegram User ID
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your user ID (a number like `123456789`)
3. Add this to `allowed_users` to restrict bot access to only you

#### Anthropic API Key
1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Go to API Keys and create a new key
3. Copy the key (starts with `sk-ant-...`)

### Optional Settings

```yaml
obsidian:
  vault_path: "/path/to/data/directory"  # Where to store data files

whisper:
  mode: "local"       # "local" (free) or "cloud" (fast, uses OpenAI API)
  openai_api_key: ""  # Required only if mode: "cloud"
  model_size: "base"  # Local mode: tiny, base, small, medium, large-v3
  device: "auto"      # Local mode: auto, cpu, cuda

# Email via Resend (recommended - easiest setup)
email:
  enabled: true
  provider: "resend"
  resend_api_key: "re_xxxxx"  # Get from resend.com

digest:
  time: "20:00"
  timezone: "America/Los_Angeles"
```

#### Email Setup (Resend - Recommended)
1. Sign up free at [resend.com](https://resend.com)
2. Go to API Keys and create a new key
3. Add to config: `resend_api_key: "re_xxxxx"`
4. Set `enabled: true`

That's it! The default `from_email` works with Resend's free tier.

#### Email Setup (Gmail - Alternative)
If you prefer Gmail SMTP:
```yaml
email:
  enabled: true
  provider: "smtp"
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  sender_email: "your-email@gmail.com"
  sender_password: "your-app-password"
```
Note: Gmail requires an [App Password](https://myaccount.google.com/apppasswords) (not your regular password).

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and instructions |
| `/podcast <url>` | Process a podcast episode |
| `/lookup` | Browse and manage saved summaries |
| `/help` | Show available commands |

### Workflow Example

1. **Send a podcast**:
   ```
   /podcast https://open.spotify.com/episode/...
   ```

2. **Wait for transcription** (progress updates shown)

3. **Review the draft summary** - You'll see a professional email-style summary

4. **Choose an action**:
   - **Approve & Save** - Save as-is
   - **Give Feedback** - Refine with natural language (e.g., "Make it shorter" or "Add more detail about the AI discussion")

5. **After saving**, you can:
   - **Edit Later** - Refine the saved summary
   - **Send as Email** - Email it to yourself
   - **Done** - Finish

6. **Use `/lookup`** anytime to:
   - View saved summaries
   - Edit with AI feedback
   - Send via email
   - Delete from history

## Supported Podcast Sources

- **Spotify** - Episode or show links
- **Apple Podcasts** - Episode links
- **RSS Feeds** - Direct feed URLs
- **Direct audio URLs** - MP3/M4A links

## Transcription Modes

### Cloud Mode (Recommended for most users)
Uses OpenAI's Whisper API - fast and works on any machine.

```yaml
whisper:
  mode: "cloud"
  openai_api_key: "sk-proj-..."  # Get from platform.openai.com/api-keys
```

**Pros:** Fast (~30 seconds for 1-hour podcast), no hardware requirements
**Cons:** Costs ~$0.006/minute (~$0.36 for 1-hour podcast)

### Local Mode (Free, privacy-focused)
Runs Whisper on your machine - free but requires decent hardware.

```yaml
whisper:
  mode: "local"
  model_size: "base"  # tiny, base, small, medium, large-v3
  device: "auto"      # auto, cpu, cuda
```

**Local model requirements:**

| Model | VRAM/RAM | Speed | Accuracy |
|-------|----------|-------|----------|
| `tiny` | ~1GB | Fastest | Basic |
| `base` | ~1GB | Fast | Good |
| `small` | ~2GB | Medium | Better |
| `medium` | ~5GB | Slow | Great |
| `large-v3` | ~10GB | Slowest | Best |

**Pros:** Free, audio stays on your machine
**Cons:** Slower (real-time or longer), requires good CPU/GPU

## Troubleshooting

### "Podcast transcription is slow"
- **Switch to cloud mode** - Set `mode: "cloud"` for fastest results
- Use a smaller Whisper model in local mode (`tiny` or `base`)
- If you have an NVIDIA GPU, set `device: "cuda"`
- Long podcasts (2+ hours) take proportionally longer in local mode

### "Can't find audio for Spotify podcast"
- Some Spotify podcasts are DRM-protected
- Try using the podcast's RSS feed URL instead
- Search for the podcast on podcasts.apple.com and use that link

### "Bot doesn't respond"
- Check that your Telegram user ID is in `allowed_users`
- Verify the bot token is correct
- Check the terminal for error messages

### "Email sending failed"
- For Gmail, you must use an App Password (not your regular password)
- Check that 2FA is enabled on your Google account
- Verify SMTP settings match your email provider

### "Out of memory during transcription"
- Use a smaller Whisper model
- Close other applications
- For very long podcasts, consider splitting the audio

## Project Structure

```
podcast-knowledge-bot/
├── src/
│   ├── bot.py              # Main Telegram bot
│   ├── processors/
│   │   └── podcast.py      # Podcast download & metadata
│   ├── ai/
│   │   └── summarizer.py   # Claude AI integration
│   └── storage/
│       └── summaries.py    # JSON-based storage
├── config.yaml.example     # Template configuration
├── pyproject.toml          # Dependencies
└── README.md
```

## Security Notes

- **Never commit `config.yaml`** - It contains your API keys
- **Use `allowed_users`** - Restrict bot access to your Telegram ID
- **App Passwords** - Never use your main email password
- The `.gitignore` excludes sensitive files by default

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run the bot in development
python -m src.bot
```

## License

MIT License - feel free to use and modify.

---

Built with [python-telegram-bot](https://python-telegram-bot.org/), [OpenAI Whisper](https://github.com/openai/whisper), and [Claude AI](https://anthropic.com).
