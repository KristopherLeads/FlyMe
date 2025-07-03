import os
import logging
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Config:
    """Application configuration"""
    arcade_api_key: str
    openai_api_key: str
    slack_bot_token: str
    slack_app_token: str
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> Optional['Config']:
        """Load configuration from environment variables"""
        return cls(
            arcade_api_key=os.getenv("ARCADE_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            slack_bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
            slack_app_token=os.getenv("SLACK_APP_TOKEN", ""),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of missing variables"""
        missing = []
        if not self.arcade_api_key:
            missing.append("ARCADE_API_KEY")
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.slack_bot_token:
            missing.append("SLACK_BOT_TOKEN")
        if not self.slack_app_token:
            missing.append("SLACK_APP_TOKEN")
        return missing


def setup_logging(level: str = "INFO"):
    """Configure application logging"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format
    )
    
    # Logger levels for noise reduction
    logging.getLogger("slack_bolt").setLevel(logging.WARNING) # Silences slackbolt messages with level warning
    logging.getLogger("slack_sdk").setLevel(logging.WARNING) # Silences sdk messages with level warning
    logging.getLogger("slack_bolt.AsyncApp").setLevel(logging.WARNING) # Silences asyncapp messages with level warning
    logging.getLogger("httpx").setLevel(logging.WARNING) # Silences httpx messages with level warning
    logging.getLogger("websocket").setLevel(logging.WARNING) # Silences websocket messages with level warning
    
    return logging.getLogger("flyme")
