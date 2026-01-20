# Podcast Email Bot - Project Documentation

## Product Requirements Document (PRD)

### Vision
A personal knowledge capture system that transforms podcast listening from passive consumption into active learning, with AI-generated summaries that can be reviewed, refined, and shared.

### Problem Statement
Podcast listeners often forget key insights days after listening. Traditional note-taking is disruptive to the listening experience. There's no easy way to capture, organize, and share podcast learnings.

### Solution
A Telegram bot that:
1. Accepts podcast links (Spotify, Apple Podcasts, RSS feeds)
2. Transcribes audio locally using Whisper (privacy-preserving)
3. Generates professional email-style summaries via Claude AI
4. Allows natural language refinement ("make it shorter", "focus on the AI discussion")
5. Learns from user feedback to improve future summaries
6. Emails summaries for easy sharing and archival

### Target User
Knowledge workers, lifelong learners, and podcast enthusiasts who want to extract and retain value from audio content.

### Success Metrics
- First-try approval rate (tracked by learning system)
- Time from podcast link to usable summary
- User engagement with feedback/refinement features

---

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  Telegram Bot   │────▶│   Processing Layer   │────▶│  JSON Storage   │
│  (Interface)    │     │                      │     │  (Summaries)    │
└─────────────────┘     │  - faster-whisper    │     └─────────────────┘
                        │  - yt-dlp            │              │
                        │  - feedparser        │              │
                        └──────────────────────┘              ▼
                                    │                 ┌─────────────────┐
                                    ▼                 │   AI Layer      │
                        ┌──────────────────────┐      │  (Claude API)   │
                        │   Learning System    │◀────▶│  - Summaries    │
                        │   (Preferences)      │      │  - Refinement   │
                        └──────────────────────┘      └─────────────────┘
```

### Tech Stack
- **Language**: Python 3.11+
- **Bot Framework**: python-telegram-bot (async)
- **Transcription**: faster-whisper (local, GPU-accelerated)
- **Audio Extraction**: yt-dlp, feedparser
- **AI**: Claude API via Anthropic SDK
- **Email**: Resend API (or SMTP)
- **Config**: Pydantic for validation

---

## Key Files

| File | Purpose |
|------|---------|
| `src/bot.py` | Main Telegram bot - handlers, conversation flows, email sending |
| `src/config.py` | Pydantic configuration models with validation |
| `src/ai/summarizer.py` | Claude API integration for generating/refining summaries |
| `src/ai/learning.py` | Feedback tracking and preference learning system |
| `src/processors/podcast.py` | Audio extraction, Whisper transcription |
| `src/storage/summaries.py` | JSON-based summary persistence |
| `config.yaml` | User configuration (gitignored - contains secrets) |
| `config.yaml.example` | Template for configuration |

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

## Learning System

The bot learns from user interactions to improve over time:

### What It Tracks
- **Length preference**: brief / medium / detailed
- **Detail level**: high-level / balanced / granular
- **Tone**: casual / professional / academic
- **Feature preferences**: timestamps, soundbites, takeaways
- **Common feedback patterns**: Actual phrases the user frequently uses

### How It Works
1. After each summary, user can approve or provide feedback
2. Feedback text is analyzed for preference signals
3. Preferences are injected into future summarizer prompts
4. Statistics tracked: approval rate, edit frequency

### Storage
Preferences saved to `data/learning.json` - persists across sessions.

---

## Key Technical Insights

### Telegram ConversationHandler Gotcha
When using `python-telegram-bot`'s ConversationHandler with callbacks triggered from background tasks (asyncio.create_task), the callbacks may not be caught by the handler. Solution: Register a standalone CallbackQueryHandler outside the ConversationHandler to catch these.

### Resend Free Tier Limitation
Resend's free tier only allows sending to the email address used to sign up. The bot handles this by:
1. Warning users about the limitation
2. Saving the email after first successful send
3. Offering quick-send button for repeat use

### Whisper Model Selection
- `tiny`/`base`: Fast, good for testing, lower accuracy
- `small`/`medium`: Balanced, recommended for production
- `large-v3`: Best accuracy, requires significant resources

### Markdown to HTML Email Conversion
Email clients render HTML better than plain text. The bot converts markdown formatting to proper HTML with inline styles for consistent rendering across email clients.

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
| `/cancel` | Cancel current operation |

### Interactive Mode Commands (during podcast session)
| Command | Description |
|---------|-------------|
| `/detail <text>` | Add a key fact or point |
| `/insight <text>` | Add a personal takeaway |
| `/end` | Generate summary with highlights |

---

## Security Considerations

### Implemented
- **Access control**: `allowed_users` whitelist in config
- **SSRF protection**: URL validation before fetching
- **Error sanitization**: No internal paths/details in user-facing errors
- **Secrets management**: All keys in gitignored config.yaml

### Config File Security
- `config.yaml` contains all secrets (gitignored)
- `config.yaml.example` is the safe template
- Never commit actual configuration

---

## Running the Bot

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the bot
python -m src.bot

# Or with explicit path
python -m src.bot --config config.yaml
```

### Keeping the Bot Running (Phone Access)

Since the bot runs locally on your Mac, it will stop responding if your Mac sleeps. To use the bot from your phone:

**Option 1: Prevent Mac Sleep (Quick Fix)**
```bash
# Keep Mac awake while bot runs (run in separate terminal)
caffeinate -i python -m src.bot
```

Or in System Settings → Energy → Turn off "Put hard disks to sleep" and set display sleep but not system sleep.

**Option 2: Run as Background Service**
```bash
# Run with nohup to survive terminal close
nohup python -m src.bot > bot.log 2>&1 &

# Check if running
ps aux | grep "src.bot"

# Stop the bot
pkill -f "src.bot"
```

**Option 3: Supervisor Mode (Most Resource Efficient)**
Run a lightweight supervisor that only starts the full bot when you need it:

```bash
# Start supervisor (uses ~5MB RAM when bot is off)
caffeinate -i python3 -m src.supervisor &
```

Then control from Telegram:
- `/poweron` - Start the full bot
- `/poweroff` - Stop the bot to save resources
- `/botstatus` - Check if bot is running

The supervisor stays running 24/7 but uses minimal resources. The full bot only runs when you're actively using it.

**Option 4: Deploy to Server (Best for 24/7 Access)**
For reliable phone access, deploy to a cloud server (DigitalOcean, AWS, etc.) or a Raspberry Pi on your local network.

---

## Development Notes

### Adding New Content Types
1. Create processor in `src/processors/`
2. Add handler in `src/bot.py`
3. Update summarizer prompt if needed
4. Add command to help text

### Modifying Summary Format
Edit the prompt in `src/ai/summarizer.py`. The learning system will inject user preferences automatically.

### Testing Transcription
```python
from src.processors.podcast import PodcastProcessor
processor = PodcastProcessor(config)
transcript = await processor.transcribe("path/to/audio.mp3")
```

---

## Future Enhancements (Ideas)
- Article extraction (trafilatura)
- X/Twitter thread capture
- Daily digest aggregation
- Obsidian vault integration
- Voice note capture
- Semantic search across all content
