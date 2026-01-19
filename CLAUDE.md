# Podcast Email Bot

A Telegram bot that transcribes podcasts, generates AI summaries, and emails them.

## Quick Reference

**GitHub**: https://github.com/noahlevine1717/podcast-email-bot

**Run the bot**:
```bash
cd /Users/noahlevine/knowledge-bot
source .venv/bin/activate
python -m src.bot
```

## Architecture

- **Telegram Bot**: python-telegram-bot library
- **Transcription**: Local Whisper (faster-whisper)
- **AI Summaries**: Claude API (Anthropic)
- **Email**: Resend API (free tier - sends only to registered email)
- **Learning**: Tracks user feedback to improve summaries over time

## Key Files

- `src/bot.py` - Main Telegram bot handlers
- `src/config.py` - Configuration loading (Pydantic)
- `src/ai/summarizer.py` - Claude API integration for summaries
- `src/ai/learning.py` - Learning system that improves with feedback
- `src/processors/podcast.py` - Podcast audio extraction and transcription
- `config.yaml` - User configuration (contains API keys - gitignored)
- `config.yaml.example` - Template for configuration

## Bot Commands

- `/start` - Welcome message
- `/help` - Show available commands
- `/podcast <url>` - Process a podcast (supports Spotify, RSS feeds)
- `/cancel` - Cancel current operation
- `/stats` - View learning statistics

## Interactive Mode

When processing a podcast, users can choose:
1. **AI-Only Mode** - Automatic transcription and summary
2. **You're Highlighting Mode** - Add your own notes while listening:
   - `/detail <text>` - Add a key fact or point
   - `/insight <text>` - Add your personal takeaway
   - `/end` - Generate summary with your highlights

## Configuration

All secrets are in `config.yaml` (gitignored). Copy from `config.yaml.example`:
- `telegram.bot_token` - From @BotFather
- `ai.anthropic_api_key` - From console.anthropic.com
- `email.resend_api_key` - From resend.com (free tier: send to your own email only)

## Notes

- Resend free tier only sends to the email you registered with (noahlevine1717@gmail.com)
- Learning system saves preferences to `data/learning.json`
- Bot remembers your email for quick-send after first use
