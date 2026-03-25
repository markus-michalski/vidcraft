"""Markdown and YAML frontmatter parsers for VidCraft project files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

# Pre-compiled patterns for performance
_RE_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_RE_HEADING = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_RE_TABLE_ROW = re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|", re.MULTILINE)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter and body from markdown text.

    Returns (metadata_dict, body_text).
    """
    match = _RE_FRONTMATTER.match(text)
    if not match:
        return {}, text

    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        meta = {}

    body = text[match.end() :]
    return meta, body


def parse_project_readme(path: Path) -> dict[str, Any]:
    """Parse a project README.md into structured data."""
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    result: dict[str, Any] = {
        "slug": path.parent.name,
        "title": meta.get("title", path.parent.name),
        "video_type": meta.get("video_type", ""),
        "status": _normalize_status(meta.get("status", "Concept")),
        "platform": meta.get("platform", ""),
        "language": meta.get("language", "de"),
        "target_audience": meta.get("target_audience", ""),
        "description": meta.get("description", ""),
        "created": str(meta.get("created", "")),
        "updated": str(meta.get("updated", "")),
    }

    # Extract episode list from body
    result["episodes"] = _extract_episode_list(body)

    return result


def parse_episode_readme(path: Path) -> dict[str, Any]:
    """Parse an episode README.md into structured data."""
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    return {
        "slug": path.parent.name,
        "title": meta.get("title", path.parent.name),
        "number": meta.get("number", 0),
        "status": _normalize_status(meta.get("status", "Not Started")),
        "duration_target": meta.get("duration_target", ""),
        "platform": meta.get("platform", ""),
        "avatar": meta.get("avatar", ""),
        "description": meta.get("description", ""),
    }


def parse_scene_file(path: Path) -> dict[str, Any]:
    """Parse a scene markdown file into structured data."""
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    return {
        "file": path.name,
        "number": meta.get("number", _extract_scene_number(path.name)),
        "title": meta.get("title", ""),
        "status": _normalize_status(meta.get("status", "Outline")),
        "duration": meta.get("duration", ""),
        "visual_type": meta.get("visual_type", ""),
        "narration": _extract_section(body, "Narration"),
        "on_screen_text": _extract_section(body, "On-Screen Text"),
        "visual_direction": _extract_section(body, "Visual Direction"),
        "assets": _extract_section(body, "Assets"),
    }


def parse_script_file(path: Path) -> dict[str, Any]:
    """Parse a script markdown file."""
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    return {
        "file": path.name,
        "status": _normalize_status(meta.get("status", "Draft")),
        "version": meta.get("version", 1),
        "word_count": len(body.split()),
        "body": body,
    }


def _extract_section(body: str, heading: str) -> str:
    """Extract content under a specific markdown heading."""
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(body)
    return match.group(1).strip() if match else ""


def _extract_episode_list(body: str) -> list[str]:
    """Extract episode slugs from a project README body."""
    episodes = []
    in_list = False
    for line in body.splitlines():
        if re.match(r"^##\s+Episodes?", line, re.IGNORECASE):
            in_list = True
            continue
        if in_list:
            if line.startswith("## "):
                break
            match = re.match(r"^\d+\.\s+\[?(.+?)\]?(?:\(.*\))?\s*[-—]", line)
            if match:
                episodes.append(match.group(1).strip())
    return episodes


def _extract_scene_number(filename: str) -> int:
    """Extract scene number from filename like '01-intro.md'."""
    match = re.match(r"^(\d+)", filename)
    return int(match.group(1)) if match else 0


# Canonical status values
_STATUS_MAP = {
    "concept": "Concept",
    "brief complete": "Brief Complete",
    "brief": "Brief Complete",
    "research done": "Research Done",
    "research": "Research Done",
    "script draft": "Script Draft",
    "draft": "Script Draft",
    "script approved": "Script Approved",
    "approved": "Script Approved",
    "storyboard done": "Storyboard Done",
    "storyboard": "Storyboard Done",
    "assets ready": "Assets Ready",
    "generated": "Generated",
    "reviewed": "Reviewed",
    "published": "Published",
    "not started": "Not Started",
    "in progress": "In Progress",
    "script written": "Script Written",
    "visual defined": "Visual Defined",
    "qa passed": "QA Passed",
    "final": "Final",
    "outline": "Outline",
}


def _normalize_status(raw: str) -> str:
    """Normalize status string to canonical form."""
    if not raw:
        return "Not Started"
    key = raw.strip().lower()
    return _STATUS_MAP.get(key, raw.strip())
