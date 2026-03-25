"""Path resolution utilities for VidCraft."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def resolve_project_content(config: dict[str, Any], project_slug: str) -> Path:
    """Resolve content root for a project."""
    return Path(config["paths"]["content_root"]) / "projects" / project_slug


def resolve_episode_path(
    config: dict[str, Any], project_slug: str, episode_slug: str
) -> Path:
    """Resolve path for an episode within a project."""
    return resolve_project_content(config, project_slug) / "episodes" / episode_slug


def resolve_scene_path(
    config: dict[str, Any],
    project_slug: str,
    episode_slug: str,
    scene_file: str,
) -> Path:
    """Resolve path for a scene file within an episode."""
    return (
        resolve_episode_path(config, project_slug, episode_slug) / "scenes" / scene_file
    )


def find_projects(config: dict[str, Any]) -> list[Path]:
    """Find all project directories under content root."""
    root = Path(config["paths"]["content_root"]) / "projects"
    if not root.exists():
        return []
    return sorted(
        p for p in root.iterdir() if p.is_dir() and (p / "README.md").exists()
    )


def find_episodes(config: dict[str, Any], project_slug: str) -> list[Path]:
    """Find all episode directories within a project."""
    episodes_dir = resolve_project_content(config, project_slug) / "episodes"
    if not episodes_dir.exists():
        return []
    return sorted(
        p for p in episodes_dir.iterdir() if p.is_dir() and (p / "README.md").exists()
    )
