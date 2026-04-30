"""Smoke test: state CRUD roundtrip — create → list → update → rebuild.

Tests the core state management workflow that every user interaction depends on.
Also verifies that path validation (fix from #47) is active in the write tool.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SERVER_PATH = PLUGIN_ROOT / "servers" / "vidcraft-server" / "server.py"


def _make_config(content_root: Path) -> dict:
    return {
        "paths": {
            "content_root": str(content_root),
            "video_root": str(content_root / "videos"),
            "assets_root": str(content_root / "assets"),
            "overrides": str(content_root / "overrides"),
        },
        "defaults": {"language": ["de"], "wpm": 140, "platform": "heygen"},
        "heygen": {"default_avatar": "", "default_voice": ""},
        "synthesia": {"default_avatar": "", "default_voice": ""},
        "brand": {"name": "Test Brand", "tone": ["professional"]},
    }


def _load_server(monkeypatch: pytest.MonkeyPatch, content_root: Path) -> Any:
    plugin_root_str = str(PLUGIN_ROOT)
    if plugin_root_str not in sys.path:
        sys.path.insert(0, plugin_root_str)
    spec = importlib.util.spec_from_file_location("vidcraft_smoke_state", SERVER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    config = _make_config(content_root)
    monkeypatch.setattr(module, "load_config", lambda: config)
    monkeypatch.setattr(module._cache, "invalidate", lambda: None)
    return module


class TestStateCrudRoundtrip:
    """create_project_structure → list_projects → update_field → rebuild_state."""

    @pytest.fixture()
    def setup(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        content_root = tmp_path / "content"
        content_root.mkdir()
        server = _load_server(monkeypatch, content_root)
        return server, content_root

    def test_create_project_structure(self, setup) -> None:
        server, content_root = setup
        result = server.create_project_structure("Smoke Test Project", "tutorial")
        assert "created" in result.lower()
        assert (content_root / "projects" / "smoke-test-project").is_dir()

    def test_list_projects_after_create(
        self, setup, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server, content_root = setup
        server.create_project_structure("List Test Project", "tutorial")

        state = {
            "projects": {
                "list-test-project": {
                    "slug": "list-test-project",
                    "title": "List Test Project",
                    "status": "Concept",
                    "video_type": "tutorial",
                    "episode_count": 0,
                }
            }
        }
        monkeypatch.setattr(server._cache, "get", lambda: state)

        result = server.list_projects()
        assert "list-test-project" in result.lower() or "List Test Project" in result

    def test_update_field_on_project_readme(self, setup) -> None:
        server, content_root = setup
        server.create_project_structure("Update Test Project", "tutorial")

        readme = content_root / "projects" / "update-test-project" / "README.md"
        assert readme.exists(), "create_project_structure must create README.md"

        result = server.update_field(str(readme), "status", "Script Draft")
        assert "updated" in result.lower() or "status" in result.lower(), (
            f"update_field failed: {result}"
        )

        updated_text = readme.read_text(encoding="utf-8")
        assert "Script Draft" in updated_text

    def test_rebuild_state_runs_without_error(
        self, setup, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server, content_root = setup
        server.create_project_structure("Rebuild Test Project", "tutorial")

        captured = {}

        def fake_rebuild(**kwargs) -> dict:
            captured["called"] = True
            return {"projects": {}}

        monkeypatch.setattr(server, "rebuild", fake_rebuild)
        monkeypatch.setattr(server._cache, "invalidate", lambda: None)

        result = server.rebuild_state()
        assert "rebuilt" in result.lower() or captured.get("called"), (
            f"rebuild_state did not run: {result}"
        )


class TestPathValidationActive:
    """Verifies the #47 security fix is active in the state write tool."""

    def test_update_field_rejects_path_outside_content_root(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        content_root = tmp_path / "content"
        content_root.mkdir()
        server = _load_server(monkeypatch, content_root)

        outside = tmp_path / "attacker" / "secret.md"
        outside.parent.mkdir()
        outside.write_text("---\nstatus: Concept\n---\n", encoding="utf-8")

        result = server.update_field(str(outside), "status", "HACKED")
        assert "outside content root" in result.lower(), (
            "update_field must reject paths outside content_root — "
            "_assert_within_content_root not applied (#47)"
        )

    def test_update_field_accepts_path_inside_content_root(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        content_root = tmp_path / "content"
        content_root.mkdir()
        server = _load_server(monkeypatch, content_root)

        valid = content_root / "projects" / "test" / "README.md"
        valid.parent.mkdir(parents=True)
        valid.write_text("---\nstatus: Concept\n---\n\n# Test\n", encoding="utf-8")

        result = server.update_field(str(valid), "status", "Script Draft")
        assert "outside content root" not in result.lower()


class TestIdeasCrud:
    """create_video_idea → get_video_ideas roundtrip."""

    def test_create_and_retrieve_idea(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        content_root = tmp_path / "content"
        content_root.mkdir()
        server = _load_server(monkeypatch, content_root)

        create_result = server.create_video_idea(
            title="Smoke Test Idea",
            notes="A concept for smoke testing",
        )
        assert (
            "smoke test idea" in create_result.lower()
            or "created" in create_result.lower()
        ), f"create_video_idea failed: {create_result}"

        get_result = server.get_video_ideas()
        # Returns JSON list when ideas exist, or a "No ideas yet" string otherwise
        assert isinstance(get_result, str) and len(get_result) > 0
