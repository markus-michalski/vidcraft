"""Configuration loading and validation for VidCraft."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

CONFIG_PATH = Path.home() / ".vidcraft" / "config.yaml"
CACHE_DIR = Path.home() / ".vidcraft" / "cache"
STATE_PATH = CACHE_DIR / "state.json"


def _expand_path(raw: str) -> Path:
    """Expand ~ and environment variables in a path string."""
    return Path(os.path.expandvars(os.path.expanduser(raw)))


def load_config() -> dict[str, Any]:
    """Load and validate configuration from ~/.vidcraft/config.yaml."""
    if not CONFIG_PATH.exists():
        return _default_config()

    with open(CONFIG_PATH, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    config = _default_config()
    _deep_merge(config, raw)

    # Expand all path values
    if "paths" in config:
        for key, val in config["paths"].items():
            if isinstance(val, str):
                config["paths"][key] = str(_expand_path(val))

    return config


def _default_config() -> dict[str, Any]:
    """Return default configuration values."""
    return {
        "paths": {
            "content_root": str(Path.home() / "video-projects"),
            "video_root": str(Path.home() / "video-projects" / "videos"),
            "assets_root": str(Path.home() / "video-projects" / "assets"),
            "overrides": str(Path.home() / "video-projects" / "overrides"),
        },
        "defaults": {
            "language": "de",
            "wpm": 140,
            "platform": "heygen",
        },
        "heygen": {
            "default_avatar": "",
            "default_voice": "",
        },
        "synthesia": {
            "default_avatar": "",
            "default_voice": "",
        },
        "brand": {
            "name": "",
            "primary_color": "",
            "secondary_color": "",
            "font": "",
            "tone": ["professional", "friendly"],
        },
    }


def _deep_merge(base: dict, override: dict) -> None:
    """Recursively merge override into base dict (mutates base)."""
    for key, val in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(val, dict):
            _deep_merge(base[key], val)
        else:
            base[key] = val


def get_content_root(config: dict[str, Any]) -> Path:
    """Return the content root path from config."""
    return Path(config["paths"]["content_root"])


def get_video_root(config: dict[str, Any]) -> Path:
    """Return the video root path from config."""
    return Path(config["paths"]["video_root"])


def get_assets_root(config: dict[str, Any]) -> Path:
    """Return the assets root path from config."""
    return Path(config["paths"]["assets_root"])


def resolve_project_path(config: dict[str, Any], project_slug: str) -> Path:
    """Resolve full path for a project's content directory."""
    return get_content_root(config) / "projects" / project_slug


def resolve_video_path(config: dict[str, Any], project_slug: str) -> Path:
    """Resolve full path for a project's video output directory."""
    return get_video_root(config) / "projects" / project_slug


def resolve_assets_path(config: dict[str, Any], project_slug: str) -> Path:
    """Resolve full path for a project's assets directory."""
    return get_assets_root(config) / "projects" / project_slug
