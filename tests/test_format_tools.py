"""Regression tests for HeyGen / Synthesia format tools.

Ensures the platform-specific format tools (heygen_format_script,
synthesia_format_script) are registered in server.py and referenced
correctly from the corresponding skills. Guards against regressions
after removal of the generic format_for_clipboard helper (issue #2).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SERVER_PATH = PLUGIN_ROOT / "servers" / "vidcraft-server" / "server.py"
SERVER_SOURCE = SERVER_PATH.read_text(encoding="utf-8")


def _load_server_module():
    tools_path = str(PLUGIN_ROOT)
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    spec = importlib.util.spec_from_file_location(
        "vidcraft_server_format_tools", SERVER_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _skill_frontmatter(skill_name: str) -> dict:
    skill_path = PLUGIN_ROOT / "skills" / skill_name / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    end = text.index("---", 3)
    return yaml.safe_load(text[3:end])


class TestServerExportsPlatformFormatters:
    def test_heygen_format_script_exists(self) -> None:
        server = _load_server_module()
        assert hasattr(server, "heygen_format_script"), (
            "heygen_format_script must be defined in server.py"
        )

    def test_synthesia_format_script_exists(self) -> None:
        server = _load_server_module()
        assert hasattr(server, "synthesia_format_script"), (
            "synthesia_format_script must be defined in server.py"
        )

    def test_heygen_format_script_registered_as_mcp_tool(self) -> None:
        # Lightweight source-level check: decorator is applied directly above def
        assert "@mcp.tool()\ndef heygen_format_script(" in SERVER_SOURCE, (
            "heygen_format_script must be decorated with @mcp.tool()"
        )

    def test_synthesia_format_script_registered_as_mcp_tool(self) -> None:
        assert "@mcp.tool()\ndef synthesia_format_script(" in SERVER_SOURCE, (
            "synthesia_format_script must be decorated with @mcp.tool()"
        )


class TestGenericFormatToolRemoved:
    """format_for_clipboard is consolidated into platform-specific tools (#2)."""

    def test_format_for_clipboard_not_registered(self) -> None:
        assert "def format_for_clipboard(" not in SERVER_SOURCE, (
            "format_for_clipboard must be removed — use "
            "heygen_format_script / synthesia_format_script instead"
        )


class TestSkillsReferencePlatformFormatters:
    def test_heygen_skill_uses_heygen_format_script(self) -> None:
        meta = _skill_frontmatter("heygen-engineer")
        allowed = meta.get("allowed-tools", [])
        assert "mcp__vidcraft-mcp__heygen_format_script" in allowed, (
            "heygen-engineer must declare mcp__vidcraft-mcp__heygen_format_script"
        )

    def test_synthesia_skill_uses_synthesia_format_script(self) -> None:
        meta = _skill_frontmatter("synthesia-engineer")
        allowed = meta.get("allowed-tools", [])
        assert "mcp__vidcraft-mcp__synthesia_format_script" in allowed, (
            "synthesia-engineer must declare mcp__vidcraft-mcp__synthesia_format_script"
        )

    @pytest.mark.parametrize("skill_name", ["heygen-engineer", "synthesia-engineer"])
    def test_skill_no_longer_references_format_for_clipboard(
        self, skill_name: str
    ) -> None:
        skill_path = PLUGIN_ROOT / "skills" / skill_name / "SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        assert "format_for_clipboard" not in text, (
            f"{skill_name}/SKILL.md still references the removed "
            f"format_for_clipboard tool"
        )
