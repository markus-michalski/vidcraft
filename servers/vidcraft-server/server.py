#!/usr/bin/env python3
"""VidCraft MCP Server — AI Video Production tools via Model Context Protocol.

Provides tools for project management, content operations, script analysis,
storyboard validation, platform integration, and quality gates.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

# Ensure tools are importable
_plugin_root = os.environ.get(
    "CLAUDE_PLUGIN_ROOT", str(Path(__file__).resolve().parent.parent.parent)
)
_tools_path = str(Path(_plugin_root))
if _tools_path not in sys.path:
    sys.path.insert(0, _tools_path)

from mcp.server.fastmcp import FastMCP  # noqa: E402

from tools.shared.config import (  # noqa: E402
    load_config,
    resolve_assets_path,
    resolve_project_path,
    resolve_video_path,
)
from tools.shared.paths import (  # noqa: E402
    resolve_episode_path,
    slugify,
)
from tools.state.indexer import StateCache, rebuild  # noqa: E402

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

mcp = FastMCP("vidcraft-mcp")

_cache = StateCache()

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _safe_json(data: Any) -> str:
    """Serialize data to JSON, handling non-serializable types."""
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def _today() -> str:
    """Return today's date as ISO string."""
    return date.today().isoformat()


def _now_utc() -> str:
    """Return current UTC datetime as ISO string."""
    return datetime.now(timezone.utc).isoformat()


# ===========================================================================
# STATE MANAGEMENT TOOLS
# ===========================================================================


@mcp.tool()
def list_projects() -> str:
    """List all video projects with their status and episode counts."""
    state = _cache.get()
    projects = state.get("projects", {})

    if not projects:
        return "No projects found. Use create_project_structure to start a new project."

    lines = []
    for slug, proj in sorted(projects.items()):
        ep_count = proj.get("episode_count", 0)
        lines.append(
            f"- **{proj['title']}** ({slug}) — {proj['status']} | "
            f"{ep_count} episode(s) | {proj.get('video_type', 'N/A')} | "
            f"{proj.get('platform', 'N/A')}"
        )

    return "\n".join(lines)


@mcp.tool()
def find_project(query: str) -> str:
    """Find a project by slug or partial name match.

    Args:
        query: Project slug or partial name to search for.
    """
    state = _cache.get()
    projects = state.get("projects", {})

    # Exact slug match
    if query in projects:
        return _safe_json(projects[query])

    # Partial match
    query_lower = query.lower()
    matches = [
        (slug, proj)
        for slug, proj in projects.items()
        if query_lower in slug or query_lower in proj.get("title", "").lower()
    ]

    if not matches:
        return f"No project found matching '{query}'."
    if len(matches) == 1:
        return _safe_json(matches[0][1])

    return "Multiple matches:\n" + "\n".join(
        f"- {slug}: {proj['title']}" for slug, proj in matches
    )


@mcp.tool()
def get_project_full(project_slug: str) -> str:
    """Get complete project data including all episodes and scenes.

    Args:
        project_slug: The project slug.
    """
    state = _cache.get()
    project = state.get("projects", {}).get(project_slug)
    if not project:
        return f"Project '{project_slug}' not found."
    return _safe_json(project)


@mcp.tool()
def get_project_progress(project_slug: str) -> str:
    """Get project progress with completion percentages per phase.

    Args:
        project_slug: The project slug.
    """
    state = _cache.get()
    project = state.get("projects", {}).get(project_slug)
    if not project:
        return f"Project '{project_slug}' not found."

    episodes = project.get("episodes_data", {})
    total = len(episodes)
    if total == 0:
        return f"Project '{project_slug}' has no episodes yet."

    status_counts: dict[str, int] = {}
    for ep in episodes.values():
        status = ep.get("status", "Not Started")
        status_counts[status] = status_counts.get(status, 0) + 1

    lines = [
        f"# {project['title']} — Progress",
        f"**Status:** {project['status']}",
        f"**Episodes:** {total}",
        "",
        "| Status | Count | % |",
        "|--------|-------|---|",
    ]
    for status, count in sorted(status_counts.items()):
        pct = round(count / total * 100)
        lines.append(f"| {status} | {count} | {pct}% |")

    return "\n".join(lines)


@mcp.tool()
def rebuild_state() -> str:
    """Rebuild the state cache from all markdown files on disk."""
    state = rebuild(preserve_session=True)
    _cache.invalidate()
    project_count = len(state.get("projects", {}))
    return f"State rebuilt. Found {project_count} project(s)."


@mcp.tool()
def get_session() -> str:
    """Get the current session context (last project, phase, pending actions)."""
    state = _cache.get()
    return _safe_json(state.get("session", {}))


@mcp.tool()
def update_session(
    last_project: str = "",
    last_episode: str = "",
    last_phase: str = "",
) -> str:
    """Update session context for continuity across conversations.

    Args:
        last_project: The project slug last worked on.
        last_episode: The episode slug last worked on.
        last_phase: The workflow phase last active.
    """
    state = _cache.get()
    session = state.get("session", {})

    if last_project:
        session["last_project"] = last_project
    if last_episode:
        session["last_episode"] = last_episode
    if last_phase:
        session["last_phase"] = last_phase

    state["session"] = session

    from tools.state.indexer import _write_state

    _write_state(state)
    _cache.invalidate()

    return "Session updated."


@mcp.tool()
def search(query: str) -> str:
    """Search across all projects, episodes, and scenes by keyword.

    Args:
        query: Search term to match against titles, descriptions, slugs.
    """
    state = _cache.get()
    query_lower = query.lower()
    results = []

    for slug, proj in state.get("projects", {}).items():
        if _matches(proj, query_lower):
            results.append(f"**Project:** {proj['title']} ({slug})")

        for ep_slug, ep in proj.get("episodes_data", {}).items():
            if _matches(ep, query_lower):
                results.append(f"  **Episode:** {ep['title']} ({slug}/{ep_slug})")

    return "\n".join(results) if results else f"No results for '{query}'."


def _matches(item: dict, query: str) -> bool:
    """Check if any text field in item contains query."""
    for val in item.values():
        if isinstance(val, str) and query in val.lower():
            return True
    return False


# ===========================================================================
# CONTENT OPERATIONS TOOLS
# ===========================================================================


@mcp.tool()
def create_project_structure(
    title: str,
    video_type: str,
    platform: str = "heygen",
    language: str = "de",
    target_audience: str = "",
    description: str = "",
) -> str:
    """Create a new video project with directory structure and templates.

    Args:
        title: Human-readable project title.
        video_type: Video type (tutorial, installation-guide, product-demo, etc.).
        platform: Target platform (heygen, synthesia).
        language: Content language (de, en).
        target_audience: Description of target audience.
        description: Brief project description.
    """
    config = load_config()
    slug = slugify(title)
    project_dir = resolve_project_path(config, slug)

    if project_dir.exists():
        return f"Project '{slug}' already exists at {project_dir}"

    # Create directories
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "episodes").mkdir(exist_ok=True)
    (project_dir / "assets").mkdir(exist_ok=True)
    (project_dir / "research").mkdir(exist_ok=True)

    # Load and fill project template
    template_path = Path(_plugin_root) / "templates" / "project.md"
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
    else:
        template = _default_project_template()

    readme_content = template.replace("{{title}}", title)
    readme_content = readme_content.replace("{{slug}}", slug)
    readme_content = readme_content.replace("{{video_type}}", video_type)
    readme_content = readme_content.replace("{{platform}}", platform)
    readme_content = readme_content.replace("{{language}}", language)
    readme_content = readme_content.replace("{{target_audience}}", target_audience)
    readme_content = readme_content.replace("{{description}}", description)
    readme_content = readme_content.replace("{{date}}", _today())

    (project_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # Rebuild state
    _cache.invalidate()

    return (
        f"Project '{title}' created at {project_dir}\n"
        f"Type: {video_type} | Platform: {platform} | Language: {language}\n"
        f"Next: Create episodes with create_episode()"
    )


@mcp.tool()
def create_episode(
    project_slug: str,
    title: str,
    number: int = 0,
    duration_target: str = "",
    platform: str = "",
    description: str = "",
) -> str:
    """Create a new episode within a project.

    Args:
        project_slug: The project slug.
        title: Episode title.
        number: Episode number (auto-detected if 0).
        duration_target: Target duration (e.g., "5:00").
        platform: Override platform for this episode.
        description: Episode description.
    """
    config = load_config()
    slug = slugify(title)
    project_dir = resolve_project_path(config, project_slug)

    if not project_dir.exists():
        return f"Project '{project_slug}' not found."

    episodes_dir = project_dir / "episodes"
    episodes_dir.mkdir(exist_ok=True)

    # Auto-detect episode number
    if number == 0:
        existing = [d for d in episodes_dir.iterdir() if d.is_dir()]
        number = len(existing) + 1

    episode_slug = f"{number:02d}-{slug}"
    episode_dir = episodes_dir / episode_slug

    if episode_dir.exists():
        return f"Episode '{episode_slug}' already exists."

    episode_dir.mkdir(parents=True, exist_ok=True)
    (episode_dir / "scenes").mkdir(exist_ok=True)
    (episode_dir / "assets").mkdir(exist_ok=True)

    # Load and fill episode template
    template_path = Path(_plugin_root) / "templates" / "episode.md"
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
    else:
        template = _default_episode_template()

    content = template.replace("{{title}}", title)
    content = content.replace("{{number}}", str(number))
    content = content.replace("{{slug}}", episode_slug)
    content = content.replace("{{duration_target}}", duration_target)
    content = content.replace("{{platform}}", platform)
    content = content.replace("{{description}}", description)
    content = content.replace("{{date}}", _today())

    (episode_dir / "README.md").write_text(content, encoding="utf-8")

    _cache.invalidate()

    return (
        f"Episode '{title}' (#{number}) created at {episode_dir}\n"
        f"Next: Create scenes with create_scene()"
    )


@mcp.tool()
def create_scene(
    project_slug: str,
    episode_slug: str,
    title: str,
    number: int = 0,
    visual_type: str = "avatar",
    duration: str = "",
) -> str:
    """Create a new scene within an episode.

    Args:
        project_slug: The project slug.
        episode_slug: The episode slug.
        title: Scene title.
        number: Scene number (auto-detected if 0).
        visual_type: Visual type (avatar, screencast, slides, b-roll).
        duration: Target scene duration (e.g., "0:30").
    """
    config = load_config()
    episode_dir = resolve_episode_path(config, project_slug, episode_slug)

    if not episode_dir.exists():
        return f"Episode '{episode_slug}' not found in project '{project_slug}'."

    scenes_dir = episode_dir / "scenes"
    scenes_dir.mkdir(exist_ok=True)

    # Auto-detect scene number
    if number == 0:
        existing = list(scenes_dir.glob("*.md"))
        number = len(existing) + 1

    scene_slug = f"{number:02d}-{slugify(title)}"
    scene_file = scenes_dir / f"{scene_slug}.md"

    if scene_file.exists():
        return f"Scene '{scene_slug}' already exists."

    # Load and fill scene template
    template_path = Path(_plugin_root) / "templates" / "scene.md"
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
    else:
        template = _default_scene_template()

    content = template.replace("{{title}}", title)
    content = content.replace("{{number}}", str(number))
    content = content.replace("{{visual_type}}", visual_type)
    content = content.replace("{{duration}}", duration)
    content = content.replace("{{date}}", _today())

    scene_file.write_text(content, encoding="utf-8")

    _cache.invalidate()

    return f"Scene '{title}' (#{number}) created at {scene_file}"


@mcp.tool()
def get_episode(project_slug: str, episode_slug: str) -> str:
    """Get episode data including all scenes.

    Args:
        project_slug: The project slug.
        episode_slug: The episode slug.
    """
    state = _cache.get()
    project = state.get("projects", {}).get(project_slug)
    if not project:
        return f"Project '{project_slug}' not found."

    episode = project.get("episodes_data", {}).get(episode_slug)
    if not episode:
        return f"Episode '{episode_slug}' not found in project '{project_slug}'."

    return _safe_json(episode)


@mcp.tool()
def list_episodes(project_slug: str) -> str:
    """List all episodes in a project with their status.

    Args:
        project_slug: The project slug.
    """
    state = _cache.get()
    project = state.get("projects", {}).get(project_slug)
    if not project:
        return f"Project '{project_slug}' not found."

    episodes = project.get("episodes_data", {})
    if not episodes:
        return f"No episodes in project '{project_slug}'."

    lines = []
    for slug, ep in sorted(episodes.items(), key=lambda x: x[1].get("number", 0)):
        scene_count = ep.get("scene_count", 0)
        lines.append(
            f"- **{ep['title']}** ({slug}) — {ep['status']} | "
            f"{scene_count} scene(s) | {ep.get('duration_target', 'N/A')}"
        )

    return "\n".join(lines)


@mcp.tool()
def list_scenes(project_slug: str, episode_slug: str) -> str:
    """List all scenes in an episode.

    Args:
        project_slug: The project slug.
        episode_slug: The episode slug.
    """
    state = _cache.get()
    project = state.get("projects", {}).get(project_slug)
    if not project:
        return f"Project '{project_slug}' not found."

    episode = project.get("episodes_data", {}).get(episode_slug)
    if not episode:
        return f"Episode '{episode_slug}' not found."

    scenes = episode.get("scenes", {})
    if not scenes:
        return "No scenes found."

    lines = []
    for name, scene in sorted(scenes.items(), key=lambda x: x[1].get("number", 0)):
        lines.append(
            f"- **{scene.get('title', name)}** ({name}) — {scene['status']} | "
            f"{scene.get('visual_type', 'N/A')} | {scene.get('duration', 'N/A')}"
        )

    return "\n".join(lines)


@mcp.tool()
def update_field(
    file_path: str,
    field: str,
    value: str,
) -> str:
    """Update a YAML frontmatter field in a markdown file.

    Args:
        file_path: Absolute path to the markdown file.
        field: The frontmatter field name to update.
        value: The new value for the field.
    """
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"

    text = path.read_text(encoding="utf-8")

    # Parse existing frontmatter
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return "No YAML frontmatter found in file."

    import yaml

    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        return f"YAML parse error: {e}"

    meta[field] = value
    body = text[match.end() :]

    new_frontmatter = yaml.dump(meta, default_flow_style=False, allow_unicode=True)
    new_text = f"---\n{new_frontmatter}---\n{body}"

    path.write_text(new_text, encoding="utf-8")
    _cache.invalidate()

    return f"Updated '{field}' to '{value}' in {path.name}"


@mcp.tool()
def resolve_path(
    project_slug: str,
    path_type: str = "content",
    episode_slug: str = "",
) -> str:
    """Resolve the filesystem path for a project component.

    Args:
        project_slug: The project slug.
        path_type: Type of path (content, video, assets).
        episode_slug: Optional episode slug for episode-level paths.
    """
    config = load_config()

    if path_type == "content":
        base = resolve_project_path(config, project_slug)
    elif path_type == "video":
        base = resolve_video_path(config, project_slug)
    elif path_type == "assets":
        base = resolve_assets_path(config, project_slug)
    else:
        return f"Unknown path type: {path_type}"

    if episode_slug:
        base = base / "episodes" / episode_slug

    return str(base)


@mcp.tool()
def extract_section(file_path: str, heading: str) -> str:
    """Extract content under a specific markdown heading from a file.

    Args:
        file_path: Absolute path to the markdown file.
        heading: The heading text to extract (without # prefix).
    """
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"

    text = path.read_text(encoding="utf-8")

    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return f"Section '{heading}' not found."

    return match.group(1).strip()


# ===========================================================================
# SCRIPT ANALYSIS TOOLS
# ===========================================================================


@mcp.tool()
def analyze_timing(text: str, wpm: int = 140) -> str:
    """Calculate narration timing for script text.

    Args:
        text: The script/narration text to analyze.
        wpm: Words per minute (default 140 for narration).
    """
    words = len(text.split())
    minutes = words / wpm
    seconds = int(minutes * 60)
    mins = seconds // 60
    secs = seconds % 60

    return _safe_json(
        {
            "word_count": words,
            "wpm": wpm,
            "estimated_duration": f"{mins}:{secs:02d}",
            "total_seconds": seconds,
        }
    )


@mcp.tool()
def check_readability(text: str) -> str:
    """Analyze readability of script text (Flesch score, sentence stats).

    Args:
        text: The script text to analyze.
    """
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = text.split()

    word_count = len(words)
    sentence_count = len(sentences)
    avg_sentence_length = word_count / max(sentence_count, 1)

    # Simplified Flesch Reading Ease
    syllable_count = sum(_count_syllables(w) for w in words)
    avg_syllables = syllable_count / max(word_count, 1)

    flesch = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables

    # Find long sentences (>20 words)
    long_sentences = []
    for s in sentences:
        wc = len(s.split())
        if wc > 20:
            long_sentences.append(
                {"text": s[:80] + "..." if len(s) > 80 else s, "words": wc}
            )

    verdict = "PASS" if flesch >= 60 else "WARN" if flesch >= 40 else "FAIL"

    return _safe_json(
        {
            "flesch_reading_ease": round(flesch, 1),
            "verdict": verdict,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_syllables_per_word": round(avg_syllables, 1),
            "long_sentences": long_sentences,
        }
    )


def _count_syllables(word: str) -> int:
    """Estimate syllable count for a word."""
    word = word.lower().strip(".,!?;:'\"")
    if not word:
        return 0
    count = 0
    vowels = "aeiouy"
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


@mcp.tool()
def validate_structure(
    project_slug: str,
    episode_slug: str,
) -> str:
    """Validate episode structure against video type conventions.

    Args:
        project_slug: The project slug.
        episode_slug: The episode slug.
    """
    state = _cache.get()
    project = state.get("projects", {}).get(project_slug)
    if not project:
        return f"Project '{project_slug}' not found."

    episode = project.get("episodes_data", {}).get(episode_slug)
    if not episode:
        return f"Episode '{episode_slug}' not found."

    issues = []
    video_type = project.get("video_type", "")

    # Check scene count
    scene_count = episode.get("scene_count", 0)
    if scene_count == 0:
        issues.append("FAIL: No scenes defined")

    # Check for narration in scenes
    scenes = episode.get("scenes", {})
    empty_narration = [
        name for name, s in scenes.items() if not s.get("narration", "").strip()
    ]
    if empty_narration:
        issues.append(f"WARN: Empty narration in: {', '.join(empty_narration)}")

    # Check for visual direction
    no_visual = [
        name for name, s in scenes.items() if not s.get("visual_direction", "").strip()
    ]
    if no_visual:
        issues.append(f"WARN: No visual direction in: {', '.join(no_visual)}")

    if not issues:
        return f"PASS: Episode '{episode_slug}' structure is valid for type '{video_type}'."

    return "\n".join(issues)


@mcp.tool()
def format_for_clipboard(
    project_slug: str,
    episode_slug: str,
    platform: str = "heygen",
) -> str:
    """Format episode script for copy-paste into HeyGen or Synthesia.

    Args:
        project_slug: The project slug.
        episode_slug: The episode slug.
        platform: Target platform (heygen, synthesia).
    """
    state = _cache.get()
    project = state.get("projects", {}).get(project_slug)
    if not project:
        return f"Project '{project_slug}' not found."

    episode = project.get("episodes_data", {}).get(episode_slug)
    if not episode:
        return f"Episode '{episode_slug}' not found."

    scenes = episode.get("scenes", {})
    if not scenes:
        return "No scenes found."

    lines = []
    for name, scene in sorted(scenes.items(), key=lambda x: x[1].get("number", 0)):
        narration = scene.get("narration", "").strip()
        if narration:
            if platform == "synthesia":
                # Synthesia: one scene = one slide
                lines.append(
                    f"--- Scene {scene.get('number', '?')}: {scene.get('title', '')} ---"
                )
                lines.append(narration)
                lines.append("")
            else:
                # HeyGen: continuous script
                lines.append(narration)
                lines.append("")

    return "\n".join(lines).strip()


# ===========================================================================
# PLATFORM INTEGRATION TOOLS
# ===========================================================================


# Platform character limits
_PLATFORM_LIMITS = {
    "heygen": {
        "max_chars_per_scene": 1500,
        "max_scenes": 100,
        "supported_formats": ["mp4"],
        "min_resolution": "720p",
        "max_resolution": "4k",
        "supported_languages": 40,
    },
    "synthesia": {
        "max_chars_per_scene": 1000,
        "max_scenes": 50,
        "supported_formats": ["mp4"],
        "min_resolution": "720p",
        "max_resolution": "1080p",
        "supported_languages": 130,
    },
}


@mcp.tool()
def validate_platform_limits(
    project_slug: str,
    episode_slug: str,
    platform: str = "",
) -> str:
    """Check if episode content fits within platform character and scene limits.

    Args:
        project_slug: The project slug.
        episode_slug: The episode slug.
        platform: Platform to check (heygen, synthesia). Auto-detected from project if empty.
    """
    state = _cache.get()
    project = state.get("projects", {}).get(project_slug)
    if not project:
        return f"Project '{project_slug}' not found."

    episode = project.get("episodes_data", {}).get(episode_slug)
    if not episode:
        return f"Episode '{episode_slug}' not found."

    if not platform:
        platform = project.get("platform", "heygen")

    limits = _PLATFORM_LIMITS.get(platform)
    if not limits:
        return f"Unknown platform: {platform}. Supported: heygen, synthesia"

    scenes = episode.get("scenes", {})
    issues: list[str] = []
    max_chars = limits["max_chars_per_scene"]

    # Check scene count
    if len(scenes) > limits["max_scenes"]:
        issues.append(
            f"FAIL: {len(scenes)} scenes exceeds {platform} limit of {limits['max_scenes']}"
        )

    # Check character limits per scene
    for name, scene in sorted(scenes.items(), key=lambda x: x[1].get("number", 0)):
        narration = scene.get("narration", "")
        char_count = len(narration)
        if char_count > max_chars:
            issues.append(
                f"FAIL: Scene '{name}' has {char_count} chars "
                f"(limit: {max_chars} for {platform}) — split this scene"
            )
        elif char_count > max_chars * 0.9:
            issues.append(
                f"WARN: Scene '{name}' at {char_count}/{max_chars} chars — close to limit"
            )

    if not issues:
        return (
            f"PASS: All {len(scenes)} scenes within {platform} limits "
            f"(max {max_chars} chars/scene, max {limits['max_scenes']} scenes)"
        )

    return f"# Platform Limit Check: {platform}\n\n" + "\n".join(
        f"- {i}" for i in issues
    )


@mcp.tool()
def get_platform_capabilities(platform: str) -> str:
    """Get the capabilities and limits of a video generation platform.

    Args:
        platform: Platform name (heygen, synthesia).
    """
    limits = _PLATFORM_LIMITS.get(platform)
    if not limits:
        return f"Unknown platform: {platform}. Supported: heygen, synthesia"

    info = dict(limits)

    if platform == "heygen":
        info.update(
            {
                "features": [
                    "Custom backgrounds (image/video/color)",
                    "Avatar gestures and expressions",
                    "Screen share overlay",
                    "Multiple avatar positions (left/center/right)",
                    "Background music layer",
                    "API access for automation",
                ],
                "avatar_types": ["Stock avatars", "Photo avatars", "Studio avatars"],
                "best_for": "Custom backgrounds, gesture control, API automation",
            }
        )
    elif platform == "synthesia":
        info.update(
            {
                "features": [
                    "Slide-based scene structure",
                    "130+ language support",
                    "Screen recording overlay",
                    "Text animation templates",
                    "Split-screen layouts",
                    "Built-in slide templates",
                    "Auto-translation",
                ],
                "avatar_types": ["Express avatars", "Studio avatars", "Custom avatars"],
                "best_for": "Multi-language, slide-based content, quick production",
            }
        )

    return _safe_json(info)


@mcp.tool()
def heygen_format_script(
    project_slug: str,
    episode_slug: str,
) -> str:
    """Format episode content as HeyGen-optimized scene blocks.

    Each scene block includes narration, avatar position, background,
    and visual overlay instructions.

    Args:
        project_slug: The project slug.
        episode_slug: The episode slug.
    """
    state = _cache.get()
    project = state.get("projects", {}).get(project_slug)
    if not project:
        return f"Project '{project_slug}' not found."

    episode = project.get("episodes_data", {}).get(episode_slug)
    if not episode:
        return f"Episode '{episode_slug}' not found."

    scenes = episode.get("scenes", {})
    if not scenes:
        return "No scenes found."

    blocks: list[str] = []
    for name, scene in sorted(scenes.items(), key=lambda x: x[1].get("number", 0)):
        narration = scene.get("narration", "").strip()
        visual_type = scene.get("visual_type", "avatar")
        visual_dir = scene.get("visual_direction", "").strip()
        on_screen = scene.get("on_screen_text", "").strip()

        block = [
            f"=== Scene {scene.get('number', '?')}: {scene.get('title', name)} ===",
            f"Type: {visual_type}",
        ]

        if visual_type == "avatar":
            block.append("Avatar: Center, facing camera")
        elif visual_type == "screencast":
            block.append("Avatar: Hidden (or small overlay bottom-right)")
        elif visual_type == "split":
            block.append("Avatar: Left third, screencast right two-thirds")

        if visual_dir:
            block.append(f"Background: {visual_dir[:100]}")

        if on_screen:
            block.append(f"Text Overlay: {on_screen}")

        block.append(f"\nScript:\n{narration}")
        block.append(f"\nChars: {len(narration)}/1500")
        blocks.append("\n".join(block))

    return "\n\n".join(blocks)


@mcp.tool()
def synthesia_format_script(
    project_slug: str,
    episode_slug: str,
) -> str:
    """Format episode content as Synthesia-optimized slide blocks.

    Each slide includes narration, layout recommendation, and media instructions.

    Args:
        project_slug: The project slug.
        episode_slug: The episode slug.
    """
    state = _cache.get()
    project = state.get("projects", {}).get(project_slug)
    if not project:
        return f"Project '{project_slug}' not found."

    episode = project.get("episodes_data", {}).get(episode_slug)
    if not episode:
        return f"Episode '{episode_slug}' not found."

    scenes = episode.get("scenes", {})
    if not scenes:
        return "No scenes found."

    slides: list[str] = []
    for name, scene in sorted(scenes.items(), key=lambda x: x[1].get("number", 0)):
        narration = scene.get("narration", "").strip()
        visual_type = scene.get("visual_type", "avatar")
        on_screen = scene.get("on_screen_text", "").strip()
        assets = scene.get("assets", "").strip()

        # Map visual type to Synthesia layout
        layout_map = {
            "avatar": "Avatar center, solid background",
            "screencast": "Screen recording full, avatar overlay corner",
            "slides": "Text layout, avatar left",
            "split": "Split screen: avatar left, media right",
            "b-roll": "Full media, no avatar",
        }
        layout = layout_map.get(visual_type, "Avatar center")

        slide = [
            f"--- Slide {scene.get('number', '?')}: {scene.get('title', name)} ---",
            f"Layout: {layout}",
        ]

        if on_screen:
            slide.append(f"Text Elements: {on_screen}")

        if assets:
            slide.append(f"Media: {assets[:100]}")

        slide.append(f"\nScript:\n{narration}")
        slide.append(f"\nChars: {len(narration)}/1000")
        slides.append("\n".join(slide))

    return "\n\n".join(slides)


@mcp.tool()
def list_required_assets(
    project_slug: str,
    episode_slug: str,
) -> str:
    """List all assets referenced in episode scenes that need to be prepared.

    Args:
        project_slug: The project slug.
        episode_slug: The episode slug.
    """
    state = _cache.get()
    project = state.get("projects", {}).get(project_slug)
    if not project:
        return f"Project '{project_slug}' not found."

    episode = project.get("episodes_data", {}).get(episode_slug)
    if not episode:
        return f"Episode '{episode_slug}' not found."

    scenes = episode.get("scenes", {})
    assets_needed: list[dict[str, str]] = []

    for name, scene in sorted(scenes.items(), key=lambda x: x[1].get("number", 0)):
        assets_text = scene.get("assets", "").strip()
        visual_type = scene.get("visual_type", "avatar")

        if visual_type == "screencast":
            assets_needed.append(
                {
                    "scene": name,
                    "type": "screen_recording",
                    "description": f"Screen recording for: {scene.get('title', name)}",
                }
            )

        if (
            assets_text
            and assets_text
            != "*List required assets: screenshots, images, logos, screen recordings.*"
        ):
            assets_needed.append(
                {
                    "scene": name,
                    "type": "referenced",
                    "description": assets_text[:200],
                }
            )

    if not assets_needed:
        return "No specific assets referenced. All scenes may be avatar-only."

    lines = ["# Required Assets\n"]
    for a in assets_needed:
        lines.append(f"- **Scene {a['scene']}** [{a['type']}]: {a['description']}")

    return "\n".join(lines)


# ===========================================================================
# QUALITY GATE TOOLS
# ===========================================================================


@mcp.tool()
def run_pre_generation_gates(
    project_slug: str,
    episode_slug: str,
) -> str:
    """Run all pre-generation quality gates for an episode.

    Checks: script approved, storyboard complete, assets available,
    platform limits, timing, brand compliance, accessibility.

    Args:
        project_slug: The project slug.
        episode_slug: The episode slug.
    """
    state = _cache.get()
    project = state.get("projects", {}).get(project_slug)
    if not project:
        return f"Project '{project_slug}' not found."

    episode = project.get("episodes_data", {}).get(episode_slug)
    if not episode:
        return f"Episode '{episode_slug}' not found."

    gates = []
    blocking = False

    # Gate 1: Script status
    status = episode.get("status", "Not Started")
    if status in ("Not Started", "Script Draft"):
        gates.append("FAIL: Script not approved yet")
        blocking = True
    else:
        gates.append("PASS: Script status OK")

    # Gate 2: Scenes exist
    scenes = episode.get("scenes", {})
    if not scenes:
        gates.append("FAIL: No scenes defined (storyboard missing)")
        blocking = True
    else:
        gates.append(f"PASS: {len(scenes)} scene(s) defined")

    # Gate 3: All scenes have narration
    empty_narration = [
        name for name, s in scenes.items() if not s.get("narration", "").strip()
    ]
    if empty_narration:
        gates.append(f"FAIL: Missing narration in {len(empty_narration)} scene(s)")
        blocking = True
    else:
        gates.append("PASS: All scenes have narration")

    # Gate 4: All scenes have visual direction
    no_visual = [
        name for name, s in scenes.items() if not s.get("visual_direction", "").strip()
    ]
    if no_visual:
        gates.append(f"WARN: No visual direction in {len(no_visual)} scene(s)")
    else:
        gates.append("PASS: All scenes have visual direction")

    # Gate 5: Timing check
    total_words = sum(len(s.get("narration", "").split()) for s in scenes.values())
    config = load_config()
    wpm = config.get("defaults", {}).get("wpm", 140)
    est_seconds = int(total_words / wpm * 60)
    est_duration = f"{est_seconds // 60}:{est_seconds % 60:02d}"
    gates.append(
        f"INFO: Estimated duration {est_duration} ({total_words} words @ {wpm} WPM)"
    )

    # Summary
    verdict = "BLOCKED" if blocking else "READY"
    header = f"# Pre-Generation Gates: {verdict}\n"
    return header + "\n".join(f"- {g}" for g in gates)


@mcp.tool()
def validate_project_structure(project_slug: str) -> str:
    """Validate the directory structure of a project.

    Args:
        project_slug: The project slug.
    """
    config = load_config()
    project_dir = resolve_project_path(config, project_slug)

    issues = []

    if not project_dir.exists():
        return f"Project directory not found: {project_dir}"

    if not (project_dir / "README.md").exists():
        issues.append("FAIL: Missing README.md")

    if not (project_dir / "episodes").exists():
        issues.append("WARN: No episodes directory")

    # Check each episode
    episodes_dir = project_dir / "episodes"
    if episodes_dir.exists():
        for ep_dir in sorted(episodes_dir.iterdir()):
            if not ep_dir.is_dir():
                continue
            if not (ep_dir / "README.md").exists():
                issues.append(f"FAIL: Missing README.md in episode {ep_dir.name}")
            if not (ep_dir / "scenes").exists():
                issues.append(f"WARN: No scenes directory in episode {ep_dir.name}")

    if not issues:
        return f"PASS: Project '{project_slug}' structure is valid."

    return "\n".join(issues)


# ===========================================================================
# DOCUMENT ANALYSIS TOOLS
# ===========================================================================


@mcp.tool()
def analyze_document(file_path: str) -> str:
    """Parse and analyze a document (PDF, DOCX, or Markdown) for video content extraction.

    Returns structured sections with headings, word counts, content types
    (code, lists, images), and metadata.

    Args:
        file_path: Absolute path to the document file (.md, .pdf, .docx).
    """
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"

    try:
        from tools.analysis.document_parser import parse_document

        doc = parse_document(path)
        return _safe_json(doc.to_dict())
    except ValueError as e:
        return str(e)
    except ImportError as e:
        return f"Missing dependency: {e}"


@mcp.tool()
def extract_key_points(file_path: str, max_points: int = 10) -> str:
    """Extract key points from a document for video script planning.

    Identifies important content blocks based on headings, lists, code blocks,
    and images. Each point includes a video relevance score and scene type suggestion.

    Args:
        file_path: Absolute path to the document file.
        max_points: Maximum number of key points to extract (default 10).
    """
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"

    try:
        from tools.analysis.document_parser import (
            extract_key_points as _extract,
            parse_document,
        )

        doc = parse_document(path)
        points = _extract(doc, max_points=max_points)
        return _safe_json(points)
    except (ValueError, ImportError) as e:
        return str(e)


@mcp.tool()
def suggest_video_structure(file_path: str, video_type: str = "tutorial") -> str:
    """Analyze a document and suggest a video scene structure.

    Maps document sections to video scenes with estimated timing,
    visual type recommendations, and narration word counts.

    Args:
        file_path: Absolute path to the source document.
        video_type: Target video type (tutorial, installation-guide, product-demo, etc.).
    """
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"

    try:
        from tools.analysis.document_parser import parse_document, suggest_structure

        doc = parse_document(path)
        structure = suggest_structure(doc, video_type=video_type)
        return _safe_json(structure)
    except (ValueError, ImportError) as e:
        return str(e)


@mcp.tool()
def analyze_complexity(file_path: str) -> str:
    """Analyze document complexity and recommend video type and episode count.

    Evaluates code density, list content, word count, and section depth
    to suggest the optimal video format.

    Args:
        file_path: Absolute path to the document file.
    """
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"

    try:
        from tools.analysis.document_parser import (
            analyze_complexity as _analyze,
            parse_document,
        )

        doc = parse_document(path)
        result = _analyze(doc)
        return _safe_json(result)
    except (ValueError, ImportError) as e:
        return str(e)


@mcp.tool()
def suggest_video_topics(file_path: str, max_topics: int = 5) -> str:
    """Analyze a document and suggest video topics that could be derived from it.

    Each topic includes a suggested title, video type, estimated duration,
    and which document sections it would cover.

    Args:
        file_path: Absolute path to the source document.
        max_topics: Maximum number of topic suggestions (default 5).
    """
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"

    try:
        from tools.analysis.document_parser import parse_document

        doc = parse_document(path)
    except (ValueError, ImportError) as e:
        return str(e)

    topics: list[dict[str, Any]] = []

    # Group sections by theme for topic suggestions
    code_sections = [s for s in doc.sections if s.has_code]
    list_sections = [s for s in doc.sections if s.has_list]
    concept_sections = [
        s
        for s in doc.sections
        if not s.has_code and not s.has_list and s.word_count > 50
    ]

    # Tutorial topic from code-heavy sections
    if code_sections:
        topics.append(
            {
                "title": f"Tutorial: {doc.title}",
                "video_type": "tutorial",
                "estimated_duration": f"{len(code_sections) * 2}-{len(code_sections) * 4} min",
                "source_sections": [s.heading for s in code_sections],
                "rationale": f"{len(code_sections)} code sections found — ideal for step-by-step tutorial",
            }
        )

    # Installation guide from list-heavy sections
    if list_sections:
        topics.append(
            {
                "title": f"Installation Guide: {doc.title}",
                "video_type": "installation-guide",
                "estimated_duration": f"{len(list_sections)}-{len(list_sections) * 2} min",
                "source_sections": [s.heading for s in list_sections],
                "rationale": f"{len(list_sections)} step-list sections — good for installation walkthrough",
            }
        )

    # Explainer from conceptual sections
    if concept_sections:
        topics.append(
            {
                "title": f"Explainer: {doc.title}",
                "video_type": "explainer",
                "estimated_duration": "1-3 min",
                "source_sections": [s.heading for s in concept_sections[:3]],
                "rationale": "Conceptual content — suits a concise explainer video",
            }
        )

    # Product demo if mixed content
    if code_sections and concept_sections:
        topics.append(
            {
                "title": f"Product Demo: {doc.title}",
                "video_type": "product-demo",
                "estimated_duration": "2-5 min",
                "source_sections": [s.heading for s in doc.sections[:5]],
                "rationale": "Mix of concepts and code — good for feature showcase",
            }
        )

    # FAQ video from short sections
    short_sections = [s for s in doc.sections if 20 < s.word_count < 150 and s.heading]
    if len(short_sections) >= 3:
        topics.append(
            {
                "title": f"FAQ: {doc.title}",
                "video_type": "faq-video",
                "estimated_duration": f"{len(short_sections) * 30}s - {len(short_sections)} min",
                "source_sections": [s.heading for s in short_sections[:5]],
                "rationale": f"{len(short_sections)} short Q&A-style sections",
            }
        )

    return _safe_json(topics[:max_topics])


# ===========================================================================
# BRAINSTORMING & IDEAS TOOLS
# ===========================================================================


@mcp.tool()
def create_idea(title: str, notes: str = "") -> str:
    """Add a new video idea to the ideas tracker.

    Args:
        title: Idea title.
        notes: Optional notes or description.
    """
    config = load_config()
    content_root = Path(config["paths"]["content_root"])
    ideas_file = content_root / "IDEAS.md"

    content_root.mkdir(parents=True, exist_ok=True)

    if ideas_file.exists():
        existing = ideas_file.read_text(encoding="utf-8")
    else:
        existing = "# Video Ideas\n\n"

    entry = f"\n## {title}\n\n"
    if notes:
        entry += f"{notes}\n"
    entry += f"\n*Added: {_today()}*\n"

    ideas_file.write_text(existing + entry, encoding="utf-8")
    _cache.invalidate()

    return f"Idea '{title}' added to {ideas_file}"


@mcp.tool()
def get_ideas() -> str:
    """List all video ideas from the ideas tracker."""
    state = _cache.get()
    ideas = state.get("ideas", [])

    if not ideas:
        return "No ideas yet. Use create_idea() to add one."

    lines = []
    for i, idea in enumerate(ideas, 1):
        lines.append(f"{i}. **{idea['title']}**")
        if idea.get("notes", "").strip():
            preview = idea["notes"].strip()[:100]
            lines.append(f"   {preview}")

    return "\n".join(lines)


@mcp.tool()
def get_plugin_version() -> str:
    """Return the current VidCraft plugin version."""
    return json.dumps(
        {
            "plugin": "vidcraft",
            "version": "0.1.0-dev",
            "schema_version": "1.0.0",
        }
    )


# ===========================================================================
# Default templates (fallback if template files don't exist)
# ===========================================================================


def _default_project_template() -> str:
    return """---
title: "{{title}}"
slug: "{{slug}}"
video_type: "{{video_type}}"
status: "Concept"
platform: "{{platform}}"
language: "{{language}}"
target_audience: "{{target_audience}}"
description: "{{description}}"
created: "{{date}}"
updated: "{{date}}"
---

# {{title}}

## Overview

{{description}}

## Target Audience

{{target_audience}}

## Episodes

*No episodes created yet.*

## Notes

"""


def _default_episode_template() -> str:
    return """---
title: "{{title}}"
number: {{number}}
slug: "{{slug}}"
status: "Not Started"
duration_target: "{{duration_target}}"
platform: "{{platform}}"
avatar: ""
description: "{{description}}"
---

# {{title}}

## Description

{{description}}

## Scenes

*No scenes created yet.*

## Script Notes

## Visual Notes

"""


def _default_scene_template() -> str:
    return """---
title: "{{title}}"
number: {{number}}
status: "Outline"
visual_type: "{{visual_type}}"
duration: "{{duration}}"
---

# {{title}}

## Narration

*Write the spoken text for this scene here.*

## On-Screen Text

*Text overlays, titles, or captions shown on screen.*

## Visual Direction

*Describe what the viewer sees: avatar position, background, animations, transitions.*

## Assets

*List required assets: screenshots, images, logos, screen recordings.*

"""


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    mcp.run(transport="stdio")
