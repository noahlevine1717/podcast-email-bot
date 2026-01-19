"""Configuration management for Knowledge Bot."""

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class TelegramConfig(BaseModel):
    """Telegram bot configuration."""

    bot_token: str
    # List of Telegram user IDs allowed to use the bot
    # Get your user ID by messaging @userinfobot on Telegram
    allowed_users: list[int] = Field(default_factory=list)


class ObsidianConfig(BaseModel):
    """Obsidian vault configuration."""

    vault_path: Path


class AIConfig(BaseModel):
    """AI/Claude configuration."""

    anthropic_api_key: str
    model: str = "claude-sonnet-4-20250514"


class WhisperConfig(BaseModel):
    """Whisper transcription configuration."""

    model_size: Literal["tiny", "base", "small", "medium", "large-v3"] = "base"
    device: str = "auto"


class DigestConfig(BaseModel):
    """Daily digest configuration."""

    time: str = "20:00"
    timezone: str = "America/Los_Angeles"


class SpotifyConfig(BaseModel):
    """Optional Spotify configuration."""

    client_id: str = ""
    client_secret: str = ""


class EmailConfig(BaseModel):
    """Optional email configuration for sending summaries."""

    enabled: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""


class Config(BaseModel):
    """Main configuration container."""

    telegram: TelegramConfig
    obsidian: ObsidianConfig
    ai: AIConfig
    whisper: WhisperConfig = Field(default_factory=WhisperConfig)
    digest: DigestConfig = Field(default_factory=DigestConfig)
    spotify: SpotifyConfig = Field(default_factory=SpotifyConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)

    @classmethod
    def load(cls, config_path: Path | str = "config.yaml") -> "Config":
        """Load configuration from YAML file.

        Secrets can be overridden via environment variables:
        - TELEGRAM_BOT_TOKEN
        - ANTHROPIC_API_KEY
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path) as f:
            data = yaml.safe_load(f)

        # Override secrets from environment variables if present
        if os.environ.get("TELEGRAM_BOT_TOKEN"):
            data["telegram"]["bot_token"] = os.environ["TELEGRAM_BOT_TOKEN"]
        if os.environ.get("ANTHROPIC_API_KEY"):
            data["ai"]["anthropic_api_key"] = os.environ["ANTHROPIC_API_KEY"]

        return cls.model_validate(data)


# Global config instance - initialized when bot starts
_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance."""
    if _config is None:
        raise RuntimeError("Configuration not initialized. Call init_config() first.")
    return _config


def init_config(config_path: Path | str = "config.yaml") -> Config:
    """Initialize the global configuration."""
    global _config
    _config = Config.load(config_path)
    return _config
