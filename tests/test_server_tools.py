"""Integration tests for the MCP tool layer in server.py.

Guards the contract between server.py (tool registration), skill files
(tool references in YAML frontmatter), and plugin.json (version).

Catches regressions like:
- Tool renames that break skill references (issue #2)
- Plugin version drift between get_plugin_version() and plugin.json (issue #1)
- Accidental tool removal

Design notes:
- Subset semantics: EXPECTED_CORE_TOOLS is a minimum guarantee — adding
  new tools never breaks the test, but removing one does.
- Source-level extraction is preferred over runtime introspection for the
  tool inventory: faster, no shared state, no FastMCP private API surface.
- Runtime import is reserved for behavioural tests (version, list_projects,
  create_project_structure) where actually executing the tool is the point.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SERVER_PATH = PLUGIN_ROOT / "servers" / "vidcraft-server" / "server.py"
PLUGIN_JSON = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
SKILLS_DIR = PLUGIN_ROOT / "skills"
SERVER_SOURCE = SERVER_PATH.read_text(encoding="utf-8")

# Matches `@mcp.tool()` followed by `def NAME(` or `async def NAME(`
# on the next line. Robust against parameter formatting / multi-line defs.
_TOOL_DEF_RE = re.compile(
    r"@mcp\.tool\(\)\s*\n\s*(?:async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
    re.MULTILINE,
)

# Matches `mcp__vidcraft-mcp__<tool_name>` references in skill files.
_SKILL_REF_RE = re.compile(r"mcp__vidcraft-mcp__([a-zA-Z_][a-zA-Z0-9_]*)")

# Minimum tool set the plugin guarantees. Adding new tools is fine; removing
# one of these requires deleting the entry here AND updating any consumers.
EXPECTED_CORE_TOOLS: frozenset[str] = frozenset(
    {
        # State management
        "list_projects",
        "find_project",
        "get_project_full",
        "get_project_progress",
        "rebuild_state",
        "get_session",
        "update_session",
        "search",
        # Content operations
        "create_project_structure",
        "create_episode",
        "create_scene",
        "get_episode",
        "list_episodes",
        "list_scenes",
        "update_field",
        "resolve_path",
        "extract_section",
        # Script analysis
        "analyze_timing",
        "check_readability",
        "validate_structure",
        # Storyboard / platform
        "validate_platform_limits",
        "get_platform_capabilities",
        "heygen_format_script",
        "synthesia_format_script",
        "list_required_assets",
        # Quality gates
        "run_pre_generation_gates",
        "validate_project_structure",
        # Document analysis
        "analyze_document",
        "extract_key_points",
        "suggest_video_structure",
        "analyze_complexity",
        "suggest_video_topics",
        # Ideas
        "create_video_idea",
        "get_video_ideas",
        # Script quality
        "check_pronunciation",
        # Meta
        "get_plugin_version",
    }
)


def _extract_registered_tool_names(source: str) -> set[str]:
    """Return names of all functions decorated with @mcp.tool() in source."""
    return set(_TOOL_DEF_RE.findall(source))


def _load_server_module() -> Any:
    """Load server.py as a module for runtime tool execution."""
    plugin_root_str = str(PLUGIN_ROOT)
    if plugin_root_str not in sys.path:
        sys.path.insert(0, plugin_root_str)
    spec = importlib.util.spec_from_file_location(
        "vidcraft_server_tool_integration", SERVER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _skill_frontmatter(skill_md: Path) -> dict[str, Any]:
    """Parse YAML frontmatter from a SKILL.md file."""
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.index("---", 3)
    return yaml.safe_load(text[3:end]) or {}


def _all_skill_files() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


# ---------------------------------------------------------------------------
# 1. Tool registration
# ---------------------------------------------------------------------------


class TestAllToolsRegistered:
    """The MCP server must expose at least the documented core tool set."""

    def test_extractor_finds_tools(self) -> None:
        # Sanity: the regex must work at all.
        tools = _extract_registered_tool_names(SERVER_SOURCE)
        assert len(tools) > 0, "Tool extraction regex matched nothing"

    def test_all_expected_core_tools_registered(self) -> None:
        registered = _extract_registered_tool_names(SERVER_SOURCE)
        missing = EXPECTED_CORE_TOOLS - registered
        assert not missing, (
            f"Core MCP tools missing from server.py: {sorted(missing)}.\n"
            f"If a tool was intentionally removed, also delete it from "
            f"EXPECTED_CORE_TOOLS in this file."
        )

    def test_minimum_tool_count(self) -> None:
        # Smoke test: catches accidental mass-deletion. Lower bound only —
        # adding tools never breaks this.
        registered = _extract_registered_tool_names(SERVER_SOURCE)
        assert len(registered) >= len(EXPECTED_CORE_TOOLS), (
            f"Only {len(registered)} tools registered, expected at least "
            f"{len(EXPECTED_CORE_TOOLS)}"
        )


# ---------------------------------------------------------------------------
# 2. Skill <-> server reference consistency (regression for issue #2)
# ---------------------------------------------------------------------------


class TestSkillReferencesMatchServer:
    """Every `mcp__vidcraft-mcp__*` reference in a SKILL.md must exist in server.py."""

    def test_every_skill_reference_resolves(self) -> None:
        registered = _extract_registered_tool_names(SERVER_SOURCE)
        broken: list[str] = []

        for skill_md in _all_skill_files():
            text = skill_md.read_text(encoding="utf-8")
            for tool_name in _SKILL_REF_RE.findall(text):
                if tool_name not in registered:
                    broken.append(
                        f"{skill_md.relative_to(PLUGIN_ROOT)}: "
                        f"references unknown tool 'mcp__vidcraft-mcp__{tool_name}'"
                    )

        assert not broken, (
            "Skill files reference MCP tools that are not registered:\n  - "
            + "\n  - ".join(broken)
        )

    def test_allowed_tools_frontmatter_resolves(self) -> None:
        # Same check, but scoped to the structured `allowed-tools:` field.
        # Catches references that live only in frontmatter (not prose).
        registered = _extract_registered_tool_names(SERVER_SOURCE)
        broken: list[str] = []

        for skill_md in _all_skill_files():
            meta = _skill_frontmatter(skill_md)
            allowed = meta.get("allowed-tools", []) or []
            for entry in allowed:
                if not isinstance(entry, str):
                    continue
                if not entry.startswith("mcp__vidcraft-mcp__"):
                    continue
                tool_name = entry.removeprefix("mcp__vidcraft-mcp__")
                if tool_name not in registered:
                    broken.append(
                        f"{skill_md.relative_to(PLUGIN_ROOT)} "
                        f"allowed-tools: '{entry}' not registered in server.py"
                    )

        assert not broken, (
            "Skill allowed-tools contain unregistered MCP tools:\n  - "
            + "\n  - ".join(broken)
        )


# ---------------------------------------------------------------------------
# 3. Version consistency (regression for issue #1)
# ---------------------------------------------------------------------------


class TestVersionConsistency:
    """get_plugin_version() and plugin.json must agree on the version."""

    def test_get_plugin_version_matches_plugin_json(self) -> None:
        plugin_meta = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
        expected_version = plugin_meta["version"]

        server = _load_server_module()
        result = json.loads(server.get_plugin_version())

        assert result["version"] == expected_version, (
            f"Version mismatch: server.get_plugin_version() returned "
            f"{result['version']!r}, plugin.json says {expected_version!r}"
        )

    def test_get_plugin_version_payload_shape(self) -> None:
        server = _load_server_module()
        result = json.loads(server.get_plugin_version())

        assert result["plugin"] == "vidcraft"
        assert result["version"] != "unknown", (
            "plugin.json could not be located by get_plugin_version()"
        )
        assert "schema_version" in result


# ---------------------------------------------------------------------------
# 4. Basic tool functionality (smoke tests)
# ---------------------------------------------------------------------------


class TestBasicToolFunctionality:
    """Light behavioural tests — proves the registered tools are actually callable."""

    def test_list_projects_empty_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        server = _load_server_module()
        # Replace cache with a stub that reports an empty project set.
        monkeypatch.setattr(server._cache, "get", lambda: {"projects": {}})

        result = server.list_projects()

        assert "No projects found" in result

    def test_create_project_structure_creates_directories(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = _load_server_module()
        content_root = tmp_path / "content"
        test_config = {
            "paths": {
                "content_root": str(content_root),
                "video_root": str(tmp_path / "videos"),
                "assets_root": str(tmp_path / "assets"),
                "overrides": str(tmp_path / "overrides"),
            },
            "defaults": {"language": ["de"], "wpm": 140, "platform": "heygen"},
            "heygen": {"default_avatar": "", "default_voice": ""},
            "synthesia": {"default_avatar": "", "default_voice": ""},
            "brand": {"name": "Test", "tone": []},
        }
        monkeypatch.setattr(server, "load_config", lambda: test_config)
        # Avoid triggering a real state rebuild against the user's cache.
        monkeypatch.setattr(server._cache, "invalidate", lambda: None)

        result = server.create_project_structure(
            title="Integration Test Project",
            video_type="tutorial",
        )

        assert "created" in result
        project_dir = content_root / "projects" / "integration-test-project"
        assert project_dir.is_dir(), f"Project dir not created at {project_dir}"
        assert (project_dir / "README.md").is_file()
        assert (project_dir / "episodes").is_dir()
        assert (project_dir / "assets").is_dir()
        assert (project_dir / "research").is_dir()

    def test_create_project_structure_idempotent_warning(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = _load_server_module()
        content_root = tmp_path / "content"
        test_config = {
            "paths": {
                "content_root": str(content_root),
                "video_root": str(tmp_path / "videos"),
                "assets_root": str(tmp_path / "assets"),
                "overrides": str(tmp_path / "overrides"),
            },
            "defaults": {"language": ["de"], "wpm": 140, "platform": "heygen"},
            "heygen": {"default_avatar": "", "default_voice": ""},
            "synthesia": {"default_avatar": "", "default_voice": ""},
            "brand": {"name": "Test", "tone": []},
        }
        monkeypatch.setattr(server, "load_config", lambda: test_config)
        monkeypatch.setattr(server._cache, "invalidate", lambda: None)

        first = server.create_project_structure("Dup Project", "tutorial")
        second = server.create_project_structure("Dup Project", "tutorial")

        assert "created" in first
        assert "already exists" in second
