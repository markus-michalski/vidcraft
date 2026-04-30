"""Smoke test: MCP server loads cleanly and all tool handlers are registered.

Verifies the most critical invariant: the server can be imported without error
and the expected minimum set of @mcp.tool() handlers is present.

If this test fails, the plugin is completely broken for the user.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SERVER_PATH = PLUGIN_ROOT / "servers" / "vidcraft-server" / "server.py"

_TOOL_DEF_RE = re.compile(
    r"@mcp\.tool\(\)\s*\n\s*(?:async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
    re.MULTILINE,
)

EXPECTED_MIN_TOOL_COUNT = 36


def _load_server() -> Any:
    plugin_root_str = str(PLUGIN_ROOT)
    if plugin_root_str not in sys.path:
        sys.path.insert(0, plugin_root_str)
    spec = importlib.util.spec_from_file_location("vidcraft_smoke_server", SERVER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestMcpServerLoads:
    """MCP server must import without error and register all tool handlers."""

    def test_server_file_exists(self) -> None:
        assert SERVER_PATH.exists(), f"server.py not found at {SERVER_PATH}"

    def test_server_imports_without_error(self) -> None:
        server = _load_server()
        assert server is not None

    def test_minimum_tool_count_in_source(self) -> None:
        source = SERVER_PATH.read_text(encoding="utf-8")
        tools = _TOOL_DEF_RE.findall(source)
        assert len(tools) >= EXPECTED_MIN_TOOL_COUNT, (
            f"Expected ≥{EXPECTED_MIN_TOOL_COUNT} @mcp.tool() handlers, "
            f"found {len(tools)}: {tools}"
        )

    def test_core_tools_present_in_source(self) -> None:
        source = SERVER_PATH.read_text(encoding="utf-8")
        tools = set(_TOOL_DEF_RE.findall(source))
        required = {
            "list_projects",
            "get_project_full",
            "create_project_structure",
            "create_episode",
            "create_scene",
            "update_field",
            "get_plugin_version",
            "rebuild_state",
            "heygen_format_script",
            "synthesia_format_script",
            "validate_project_structure",
            "run_pre_generation_gates",
            "analyze_document",
            "extract_key_points",
            "suggest_video_structure",
            "analyze_complexity",
            "suggest_video_topics",
        }
        missing = required - tools
        assert not missing, f"Missing required MCP tools: {missing}"

    def test_server_has_path_validation_helper(self) -> None:
        source = SERVER_PATH.read_text(encoding="utf-8")
        assert "_assert_within_content_root" in source, (
            "Security helper _assert_within_content_root missing — "
            "file_path tools are unprotected (fix from #47)"
        )

    def test_file_path_tools_use_validation(self) -> None:
        source = SERVER_PATH.read_text(encoding="utf-8")
        file_path_tools = [
            "update_field",
            "extract_section",
            "analyze_document",
            "extract_key_points",
            "suggest_video_structure",
            "analyze_complexity",
            "suggest_video_topics",
        ]
        for tool in file_path_tools:
            # Slice the section of source that belongs to this tool function
            start = source.find(f"def {tool}(")
            assert start != -1, f"Tool {tool} not found in server.py"
            # Next function starts at the next @mcp.tool() or end of file
            next_tool = source.find("@mcp.tool()", start + 1)
            section = source[start:next_tool] if next_tool != -1 else source[start:]
            assert "_assert_within_content_root" in section, (
                f"Tool '{tool}' does not call _assert_within_content_root — "
                f"path validation missing (fix from #47)"
            )
