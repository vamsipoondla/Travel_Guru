"""Configuration management for Flight Compensation Generator."""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class APIConfig:
    """API configuration settings."""
    aviationstack_key: Optional[str] = None
    flightaware_key: Optional[str] = None
    flightaware_username: Optional[str] = None


@dataclass
class AppConfig:
    """Application configuration."""
    api: APIConfig
    default_language: str = "en"
    claim_years_limit: int = 6

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "AppConfig":
        """Load configuration from file and environment variables."""
        config_data = {}

        # Try to load from config file
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"

        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}

        # API configuration with environment variable fallbacks
        api_config = config_data.get('api', {})
        api = APIConfig(
            aviationstack_key=os.environ.get('AVIATIONSTACK_API_KEY', api_config.get('aviationstack_key')),
            flightaware_key=os.environ.get('FLIGHTAWARE_API_KEY', api_config.get('flightaware_key')),
            flightaware_username=os.environ.get('FLIGHTAWARE_USERNAME', api_config.get('flightaware_username')),
        )

        return cls(
            api=api,
            default_language=config_data.get('default_language', 'en'),
            claim_years_limit=config_data.get('claim_years_limit', 6),
        )

    def has_flight_api(self) -> bool:
        """Check if any flight API is configured."""
        return bool(self.api.aviationstack_key or self.api.flightaware_key)


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig.load()
    return _config
