"""Tests for file_path security validation (issue #47).

Verifies that _assert_within_content_root rejects paths outside content_root
and that all seven affected MCP tools use it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SERVER_PATH = PLUGIN_ROOT / "servers" / "vidcraft-server" / "server.py"


def _load_server(monkeypatch: pytest.MonkeyPatch, content_root: Path) -> Any:
    plugin_root_str = str(PLUGIN_ROOT)
    if plugin_root_str not in sys.path:
        sys.path.insert(0, plugin_root_str)
    spec = importlib.util.spec_from_file_location(
        "vidcraft_server_path_val", SERVER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    config = {
        "paths": {
            "content_root": str(content_root),
            "video_root": str(content_root / "videos"),
            "assets_root": str(content_root / "assets"),
            "overrides": str(content_root / "overrides"),
        },
        "defaults": {"language": ["de"], "wpm": 140, "platform": "heygen"},
        "heygen": {"default_avatar": "", "default_voice": ""},
        "synthesia": {"default_avatar": "", "default_voice": ""},
        "brand": {"name": "Test", "tone": []},
    }
    monkeypatch.setattr(module, "load_config", lambda: config)
    return module


# ---------------------------------------------------------------------------
# Unit tests for _assert_within_content_root
# ---------------------------------------------------------------------------


class TestAssertWithinContentRoot:
    """Unit tests for the path-validation helper."""

    def test_valid_path_returns_resolved_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        content_root = tmp_path / "content"
        content_root.mkdir()
        server = _load_server(monkeypatch, content_root)

        valid_file = content_root / "projects" / "test.md"
        result = server._assert_within_content_root(str(valid_file))

        assert result == valid_file.resolve()

    def test_path_outside_content_root_raises(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        content_root = tmp_path / "content"
        content_root.mkdir()
        server = _load_server(monkeypatch, content_root)

        with pytest.raises(ValueError, match="outside content root"):
            server._assert_within_content_root("/etc/passwd")

    def test_path_traversal_is_blocked(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        content_root = tmp_path / "content"
        content_root.mkdir()
        server = _load_server(monkeypatch, content_root)

        traversal = str(content_root / ".." / ".." / "etc" / "passwd")
        with pytest.raises(ValueError, match="outside content root"):
            server._assert_within_content_root(traversal)

    def test_sibling_directory_with_shared_prefix_is_blocked(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Guards against startswith() prefix collision: /content vs /content_evil."""
        content_root = tmp_path / "content"
        content_root.mkdir()
        evil_sibling = tmp_path / "content_evil"
        evil_sibling.mkdir()
        server = _load_server(monkeypatch, content_root)

        with pytest.raises(ValueError, match="outside content root"):
            server._assert_within_content_root(str(evil_sibling / "secret.md"))

    def test_symlink_outside_content_root_is_blocked(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        content_root = tmp_path / "content"
        content_root.mkdir()
        outside_file = tmp_path / "secret.txt"
        outside_file.write_text("secret", encoding="utf-8")
        symlink = content_root / "symlink.md"
        symlink.symlink_to(outside_file)
        server = _load_server(monkeypatch, content_root)

        with pytest.raises(ValueError, match="outside content root"):
            server._assert_within_content_root(str(symlink))


# ---------------------------------------------------------------------------
# Integration: tools reject paths outside content_root
# ---------------------------------------------------------------------------


_TOOLS_WITH_FILE_PATH = [
    "update_field",
    "extract_section",
    "analyze_document",
    "extract_key_points",
    "suggest_video_structure",
    "analyze_complexity",
    "suggest_video_topics",
]


class TestToolsRejectExternalPaths:
    """Each affected tool must return an error string for paths outside content_root."""

    @pytest.fixture()
    def content_root(self, tmp_path: Path) -> Path:
        root = tmp_path / "content"
        root.mkdir()
        return root

    @pytest.fixture()
    def outside_path(self, tmp_path: Path) -> str:
        """A .md file path that exists outside content_root (sibling dir)."""
        sibling = tmp_path / "attacker"
        sibling.mkdir()
        outside = sibling / "secret.md"
        outside.write_text("secret data", encoding="utf-8")
        return str(outside)

    @pytest.fixture()
    def server(self, content_root: Path, monkeypatch: pytest.MonkeyPatch) -> Any:
        return _load_server(monkeypatch, content_root)

    def test_update_field_rejects_external_path(
        self, server: Any, outside_path: str
    ) -> None:
        result = server.update_field(outside_path, "status", "Draft")
        assert "outside content root" in result.lower()

    def test_extract_section_rejects_external_path(
        self, server: Any, outside_path: str
    ) -> None:
        result = server.extract_section(outside_path, "Overview")
        assert "outside content root" in result.lower()

    def test_analyze_document_rejects_external_path(
        self, server: Any, outside_path: str
    ) -> None:
        result = server.analyze_document(outside_path)
        assert "outside content root" in result.lower()

    def test_extract_key_points_rejects_external_path(
        self, server: Any, outside_path: str
    ) -> None:
        result = server.extract_key_points(outside_path)
        assert "outside content root" in result.lower()

    def test_suggest_video_structure_rejects_external_path(
        self, server: Any, outside_path: str
    ) -> None:
        result = server.suggest_video_structure(outside_path)
        assert "outside content root" in result.lower()

    def test_analyze_complexity_rejects_external_path(
        self, server: Any, outside_path: str
    ) -> None:
        result = server.analyze_complexity(outside_path)
        assert "outside content root" in result.lower()

    def test_suggest_video_topics_rejects_external_path(
        self, server: Any, outside_path: str
    ) -> None:
        result = server.suggest_video_topics(outside_path)
        assert "outside content root" in result.lower()

    @pytest.mark.parametrize("tool_name", _TOOLS_WITH_FILE_PATH)
    def test_all_tools_accept_valid_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tool_name: str
    ) -> None:
        """Valid paths inside content_root must not be rejected (only fail on missing file)."""
        content_root = tmp_path / "content"
        content_root.mkdir()
        server = _load_server(monkeypatch, content_root)
        valid_path = str(content_root / "projects" / "test.md")

        tool_fn = getattr(server, tool_name)
        if tool_name == "update_field":
            result = tool_fn(valid_path, "status", "Draft")
        elif tool_name == "extract_section":
            result = tool_fn(valid_path, "Overview")
        else:
            result = tool_fn(valid_path)

        assert "outside content root" not in result.lower()
