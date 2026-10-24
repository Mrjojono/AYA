"""Configuration for barcode sources."""

import os
from pathlib import Path

import yaml


def load_sources_config() -> dict:
    """Load sources configuration."""
    config_path = Path("sources.yaml")
    if not config_path.exists():
        config_path = Path("/home/joan/Projects/AYA/sources.yaml")
    if config_path.exists():
        with config_path.open() as f:
            return yaml.safe_load(f) or {}
    return {
        "barcode": {
            "order": [
                "cache",
                "interne_valide",
                "off_local",
                "gs1_gepir",
                "api_commerciale",
            ],
            "stop_on_first_valid": True,
            "timeout_per_source_s": 3,
        },
        "search": {
            "order": ["interne_valide", "off_local", "api_commerciale"],
            "parallel_for_search": True,
        },
    }


def is_commercial_enabled() -> bool:
    """Check if commercial API is enabled."""
    return os.getenv("AYA_BARCODE_COMMERCIAL_ENABLED", "false").lower() in (
        "true",
        "1",
        "yes",
    )
