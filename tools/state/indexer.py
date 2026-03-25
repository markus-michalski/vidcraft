"""State indexer for VidCraft — builds and maintains the state cache.

Scans the content directory for projects, episodes, and scenes,
then writes a consolidated state.json for fast MCP tool queries.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.shared.config import CACHE_DIR, STATE_PATH, load_config
from tools.state.parsers import (
    parse_episode_readme,
    parse_project_readme,
    parse_scene_file,
)

SCHEMA_VERSION = "1.0.0"
PLUGIN_VERSION = "0.1.0-dev"


class StateCache:
    """Thread-safe in-memory state cache with staleness detection."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state: dict[str, Any] | None = None
        self._state_mtime: float = 0.0
        self._config_mtime: float = 0.0

    def get(self) -> dict[str, Any]:
        """Get current state, rebuilding if stale."""
        with self._lock:
            if self._is_stale():
                self._state = self._load_or_rebuild()
            return self._state or {}

    def invalidate(self) -> None:
        """Force a rebuild on next access."""
        with self._lock:
            self._state = None
            self._state_mtime = 0.0

    def _is_stale(self) -> bool:
        """Check if cached state is stale."""
        if self._state is None:
            return True

        # Check state file modification
        if STATE_PATH.exists():
            mtime = STATE_PATH.stat().st_mtime
            if mtime > self._state_mtime:
                return True

        # Check config modification
        from tools.shared.config import CONFIG_PATH

        if CONFIG_PATH.exists():
            mtime = CONFIG_PATH.stat().st_mtime
            if mtime > self._config_mtime:
                return True

        return False

    def _load_or_rebuild(self) -> dict[str, Any]:
        """Load from cache file or rebuild from scratch."""
        if STATE_PATH.exists():
            try:
                data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
                if data.get("schema_version") == SCHEMA_VERSION:
                    self._state_mtime = STATE_PATH.stat().st_mtime
                    from tools.shared.config import CONFIG_PATH

                    if CONFIG_PATH.exists():
                        self._config_mtime = CONFIG_PATH.stat().st_mtime
                    return data
            except (json.JSONDecodeError, KeyError):
                pass

        # Rebuild from filesystem
        state = build_state()
        self._state_mtime = STATE_PATH.stat().st_mtime if STATE_PATH.exists() else 0.0
        return state


def build_state() -> dict[str, Any]:
    """Build complete state from content directory and write to cache."""
    config = load_config()
    content_root = Path(config["paths"]["content_root"])
    projects_dir = content_root / "projects"

    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plugin_version": PLUGIN_VERSION,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "config": config,
        "projects": {},
        "ideas": [],
        "session": {
            "last_project": "",
            "last_episode": "",
            "last_phase": "",
            "pending_actions": [],
        },
    }

    if projects_dir.exists():
        state["projects"] = _scan_projects(projects_dir)

    # Scan ideas
    ideas_file = content_root / "IDEAS.md"
    if ideas_file.exists():
        state["ideas"] = _scan_ideas(ideas_file)

    # Write to cache
    _write_state(state)

    return state


def rebuild(preserve_session: bool = True) -> dict[str, Any]:
    """Rebuild state, optionally preserving session data."""
    old_session = {}
    if preserve_session and STATE_PATH.exists():
        try:
            old = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            old_session = old.get("session", {})
        except (json.JSONDecodeError, KeyError):
            pass

    state = build_state()

    if preserve_session and old_session:
        state["session"] = old_session

    _write_state(state)
    return state


def _scan_projects(projects_dir: Path) -> dict[str, Any]:
    """Scan all project directories."""
    projects = {}

    for project_dir in sorted(projects_dir.iterdir()):
        readme = project_dir / "README.md"
        if not project_dir.is_dir() or not readme.exists():
            continue

        project = parse_project_readme(readme)
        slug = project["slug"]

        # Scan episodes
        episodes_dir = project_dir / "episodes"
        if episodes_dir.exists():
            project["episodes_data"] = _scan_episodes(episodes_dir)
            project["episode_count"] = len(project["episodes_data"])
        else:
            project["episodes_data"] = {}
            project["episode_count"] = 0

        projects[slug] = project

    return projects


def _scan_episodes(episodes_dir: Path) -> dict[str, Any]:
    """Scan all episodes within a project."""
    episodes = {}

    for ep_dir in sorted(episodes_dir.iterdir()):
        readme = ep_dir / "README.md"
        if not ep_dir.is_dir() or not readme.exists():
            continue

        episode = parse_episode_readme(readme)
        slug = episode["slug"]

        # Scan scenes
        scenes_dir = ep_dir / "scenes"
        if scenes_dir.exists():
            episode["scenes"] = _scan_scenes(scenes_dir)
            episode["scene_count"] = len(episode["scenes"])
        else:
            episode["scenes"] = {}
            episode["scene_count"] = 0

        episodes[slug] = episode

    return episodes


def _scan_scenes(scenes_dir: Path) -> dict[str, Any]:
    """Scan all scene files within an episode."""
    scenes = {}

    for scene_file in sorted(scenes_dir.glob("*.md")):
        scene = parse_scene_file(scene_file)
        scenes[scene_file.stem] = scene

    return scenes


def _scan_ideas(ideas_file: Path) -> list[dict[str, str]]:
    """Parse IDEAS.md into a list of idea entries."""
    text = ideas_file.read_text(encoding="utf-8")
    ideas = []
    current: dict[str, str] = {}

    for line in text.splitlines():
        if line.startswith("## "):
            if current:
                ideas.append(current)
            current = {"title": line[3:].strip(), "notes": ""}
        elif current:
            current["notes"] += line + "\n"

    if current:
        ideas.append(current)

    return ideas


def _write_state(state: dict[str, Any]) -> None:
    """Write state to cache file."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
