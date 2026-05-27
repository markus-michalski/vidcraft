"""Regression tests for HeyGen / Synthesia format tools.

Ensures the platform-specific format tools (heygen_format_script,
synthesia_format_script) are registered in server.py and referenced
correctly from the corresponding skills. Guards against regressions
after removal of the generic format_for_clipboard helper (issue #2).

Also covers SSML auto-conversion (#37): [pause Xs] in narration must be
converted to platform-specific SSML break tags before the output is returned.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

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


# ---------------------------------------------------------------------------
# SSML auto-conversion (#37)
# ---------------------------------------------------------------------------


def _make_state_with_narration(narration: str) -> dict[str, Any]:
    """Minimal in-memory state for formatter tests."""
    return {
        "projects": {
            "test-proj": {
                "slug": "test-proj",
                "episodes_data": {
                    "ep-01": {
                        "scenes": {
                            "01-scene": {
                                "number": 1,
                                "title": "Scene One",
                                "narration": narration,
                                "visual_type": "avatar",
                                "on_screen_text": "",
                                "visual_direction": "",
                                "assets": "",
                            }
                        }
                    }
                },
            }
        }
    }


class TestConvertPausesToSsml:
    """Unit tests for the _convert_pauses_to_ssml helper (#37)."""

    def test_function_exists_in_server(self) -> None:
        server = _load_server_module()
        assert hasattr(server, "_convert_pauses_to_ssml"), (
            "_convert_pauses_to_ssml must be defined in server.py"
        )

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("[pause 1s]", '<break time="1s"/>'),
            ("[pause 0.5s]", '<break time="0.5s"/>'),
            ("[pause 2s]", '<break time="2s"/>'),
            ("[pause 1.5s]", '<break time="1.5s"/>'),
        ],
    )
    def test_single_pause_converted(self, raw: str, expected: str) -> None:
        server = _load_server_module()
        assert server._convert_pauses_to_ssml(raw) == expected

    def test_multiple_pauses_converted(self) -> None:
        server = _load_server_module()
        text = "Click Save. [pause 1s] Now open the next step. [pause 0.5s] Done."
        result = server._convert_pauses_to_ssml(text)
        assert '<break time="1s"/>' in result
        assert '<break time="0.5s"/>' in result
        assert "[pause" not in result

    def test_no_pause_unchanged(self) -> None:
        server = _load_server_module()
        text = "Hello world. This is a test."
        assert server._convert_pauses_to_ssml(text) == text


class TestSynthesiaFormatterSsmlConversion:
    """synthesia_format_script must auto-convert [pause Xs] in output (#37)."""

    def test_pause_converted_to_break_tag(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = _load_server_module()
        narration = "Click Save. [pause 1s] The file is now updated."
        monkeypatch.setattr(
            server._cache, "get", lambda: _make_state_with_narration(narration)
        )
        result = server.synthesia_format_script("test-proj", "ep-01")
        assert '<break time="1s"/>' in result, (
            'synthesia_format_script must convert [pause Xs] to <break time="Xs"/>'
        )
        assert "[pause 1s]" not in result, (
            "Raw [pause Xs] must not appear in synthesia output"
        )

    def test_multiple_pauses_all_converted(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = _load_server_module()
        narration = "Step one. [pause 0.5s] Step two. [pause 2s] Step three."
        monkeypatch.setattr(
            server._cache, "get", lambda: _make_state_with_narration(narration)
        )
        result = server.synthesia_format_script("test-proj", "ep-01")
        assert '<break time="0.5s"/>' in result
        assert '<break time="2s"/>' in result
        assert "[pause" not in result


class TestHeyGenFormatterSsmlConversion:
    """heygen_format_script must auto-convert [pause Xs] in output (#37).

    HeyGen pause/SSML only works with Custom Voices. The formatter must
    add a caveat note in the block output so the engineer is reminded.
    """

    def test_pause_converted_to_break_tag(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = _load_server_module()
        narration = "Click Save. [pause 1s] The file is now updated."
        monkeypatch.setattr(
            server._cache, "get", lambda: _make_state_with_narration(narration)
        )
        result = server.heygen_format_script("test-proj", "ep-01")
        assert '<break time="1s"/>' in result, (
            'heygen_format_script must convert [pause Xs] to <break time="Xs"/>'
        )
        assert "[pause 1s]" not in result, (
            "Raw [pause Xs] must not appear in HeyGen output"
        )

    def test_custom_voice_caveat_present_when_pauses_exist(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = _load_server_module()
        narration = "Open the menu. [pause 1s] Select Settings."
        monkeypatch.setattr(
            server._cache, "get", lambda: _make_state_with_narration(narration)
        )
        result = server.heygen_format_script("test-proj", "ep-01")
        assert "Custom Voice" in result, (
            "heygen_format_script must add a Custom Voice caveat when "
            "SSML break tags are present"
        )

    def test_no_caveat_when_no_pauses(self, monkeypatch: pytest.MonkeyPatch) -> None:
        server = _load_server_module()
        narration = "Hello world. This is a clean script without pauses."
        monkeypatch.setattr(
            server._cache, "get", lambda: _make_state_with_narration(narration)
        )
        result = server.heygen_format_script("test-proj", "ep-01")
        # No SSML injected → no caveat needed
        assert "<break" not in result


# ---------------------------------------------------------------------------
# Variable injection (#36)
# ---------------------------------------------------------------------------


class TestHeyGenVariableExtraction:
    """heygen_format_script must detect {{variable}} placeholders and list them."""

    def test_single_variable_listed_in_summary(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = _load_server_module()
        narration = "Hey {{first_name}}, welcome to the platform!"
        monkeypatch.setattr(
            server._cache, "get", lambda: _make_state_with_narration(narration)
        )
        result = server.heygen_format_script("test-proj", "ep-01")
        assert "=== Variables Found ===" in result, (
            "heygen_format_script must include a Variables Found section"
        )
        assert "first_name" in result.split("=== Variables Found ===")[1], (
            "first_name must appear in the Variables Found section"
        )

    def test_multiple_variables_all_in_summary(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = _load_server_module()
        narration = "Hello {{first_name}}, your plan is {{plan_name}}. Renews on {{renewal_date}}."
        monkeypatch.setattr(
            server._cache, "get", lambda: _make_state_with_narration(narration)
        )
        result = server.heygen_format_script("test-proj", "ep-01")
        assert "=== Variables Found ===" in result
        summary = result.split("=== Variables Found ===")[1]
        for var in ("first_name", "plan_name", "renewal_date"):
            assert var in summary, f"Variable '{var}' must appear in Variables Found"

    def test_duplicate_variables_listed_once_in_summary(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = _load_server_module()
        narration = "Hi {{first_name}}! Great to see you, {{first_name}}."
        monkeypatch.setattr(
            server._cache, "get", lambda: _make_state_with_narration(narration)
        )
        result = server.heygen_format_script("test-proj", "ep-01")
        assert "=== Variables Found ===" in result
        summary = result.split("=== Variables Found ===")[1]
        # deduplicated — only one entry
        assert summary.count("first_name") == 1, (
            "Duplicate variables must be listed only once in the summary"
        )

    def test_no_variables_no_variable_block(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server = _load_server_module()
        narration = "Hello world. This script has no variables."
        monkeypatch.setattr(
            server._cache, "get", lambda: _make_state_with_narration(narration)
        )
        result = server.heygen_format_script("test-proj", "ep-01")
        assert "=== Variables Found ===" not in result, (
            "No variable block should appear when script has no {{placeholders}}"
        )


class TestFormatHeygenSceneHelper:
    """Unit tests for the extracted _format_heygen_scene helper."""

    def test_avatar_type_adds_center_position(self) -> None:
        server = _load_server_module()
        scene = {
            "number": 1,
            "title": "Intro",
            "narration": "Hello.",
            "visual_type": "avatar",
            "visual_direction": "",
            "on_screen_text": "",
        }
        result = server._format_heygen_scene("01-intro", scene)
        assert "Avatar: Center, facing camera" in result

    def test_screencast_type_hides_avatar(self) -> None:
        server = _load_server_module()
        scene = {
            "number": 1,
            "title": "Demo",
            "narration": "Watch this.",
            "visual_type": "screencast",
            "visual_direction": "",
            "on_screen_text": "",
        }
        result = server._format_heygen_scene("01-demo", scene)
        assert "Avatar: Hidden" in result

    def test_split_type_positions_avatar_left(self) -> None:
        server = _load_server_module()
        scene = {
            "number": 1,
            "title": "Split",
            "narration": "Left right.",
            "visual_type": "split",
            "visual_direction": "",
            "on_screen_text": "",
        }
        result = server._format_heygen_scene("01-split", scene)
        assert "Avatar: Left third" in result

    def test_visual_dir_truncated_to_100_chars(self) -> None:
        server = _load_server_module()
        long_dir = "x" * 200
        scene = {
            "number": 1,
            "title": "T",
            "narration": "N.",
            "visual_type": "avatar",
            "visual_direction": long_dir,
            "on_screen_text": "",
        }
        result = server._format_heygen_scene("01", scene)
        assert f"Background: {'x' * 100}" in result
        assert "x" * 101 not in result

    def test_on_screen_text_included(self) -> None:
        server = _load_server_module()
        scene = {
            "number": 1,
            "title": "T",
            "narration": "N.",
            "visual_type": "avatar",
            "visual_direction": "",
            "on_screen_text": "Click here",
        }
        result = server._format_heygen_scene("01", scene)
        assert "Text Overlay: Click here" in result

    def test_break_tag_triggers_caveat(self) -> None:
        server = _load_server_module()
        scene = {
            "number": 1,
            "title": "T",
            "narration": 'Go.<break time="1s"/>Done.',
            "visual_type": "avatar",
            "visual_direction": "",
            "on_screen_text": "",
        }
        result = server._format_heygen_scene("01", scene)
        assert "Custom Voice" in result

    def test_no_break_no_caveat(self) -> None:
        server = _load_server_module()
        scene = {
            "number": 1,
            "title": "T",
            "narration": "Simple narration.",
            "visual_type": "avatar",
            "visual_direction": "",
            "on_screen_text": "",
        }
        result = server._format_heygen_scene("01", scene)
        assert "Custom Voice" not in result


class TestCollectHeygenVariablesHelper:
    """Unit tests for the extracted _collect_heygen_variables helper."""

    def test_collects_variables_from_narration(self) -> None:
        server = _load_server_module()
        scenes = {"s1": {"narration": "Hello {{first_name}}!", "on_screen_text": ""}}
        result = server._collect_heygen_variables(scenes)
        assert result == {"first_name"}

    def test_collects_variables_from_on_screen_text(self) -> None:
        server = _load_server_module()
        scenes = {"s1": {"narration": "", "on_screen_text": "Welcome {{company}}"}}
        result = server._collect_heygen_variables(scenes)
        assert result == {"company"}

    def test_deduplicates_across_scenes(self) -> None:
        server = _load_server_module()
        scenes = {
            "s1": {"narration": "Hi {{name}}", "on_screen_text": ""},
            "s2": {"narration": "Bye {{name}} and {{team}}", "on_screen_text": ""},
        }
        result = server._collect_heygen_variables(scenes)
        assert result == {"name", "team"}

    def test_returns_empty_set_when_no_variables(self) -> None:
        server = _load_server_module()
        scenes = {"s1": {"narration": "No vars here.", "on_screen_text": ""}}
        result = server._collect_heygen_variables(scenes)
        assert result == set()
