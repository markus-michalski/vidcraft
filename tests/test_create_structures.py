"""Tests for create_project_structure / create_episode / create_scene template handling.

These tests cover the template loading logic in server.py, specifically:
- Template file present -> content is rendered with placeholders replaced
- Template file missing -> actionable error is returned (no silent fallback)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

# Add server module to path
_SERVER_DIR = Path(__file__).resolve().parent.parent / "servers" / "vidcraft-server"
if str(_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVER_DIR))

import server  # noqa: E402


@pytest.fixture
def tmp_plugin_root(tmp_path: Path) -> Path:
    """Create an isolated plugin root with an empty templates directory."""
    plugin = tmp_path / "plugin"
    plugin.mkdir()
    (plugin / "templates").mkdir()
    return plugin


@pytest.fixture
def patched_server(
    monkeypatch: pytest.MonkeyPatch,
    tmp_plugin_root: Path,
    mock_config: dict[str, Any],
) -> Any:
    """Isolate server module: mock plugin root, config, and cache side effects."""
    monkeypatch.setattr(server, "_plugin_root", str(tmp_plugin_root))
    monkeypatch.setattr(server, "load_config", lambda: mock_config)
    monkeypatch.setattr(server._cache, "invalidate", lambda: None)
    return server


def _write_template(plugin_root: Path, name: str, content: str) -> None:
    (plugin_root / "templates" / name).write_text(content, encoding="utf-8")


class TestCreateProjectStructureTemplate:
    def test_renders_template_when_file_present(
        self,
        patched_server: Any,
        tmp_plugin_root: Path,
        tmp_content_root: Path,
    ) -> None:
        _write_template(
            tmp_plugin_root,
            "project.md",
            "# {{title}}\nslug: {{slug}}\ntype: {{video_type}}\n",
        )

        result = patched_server.create_project_structure(
            title="My Tutorial",
            video_type="tutorial",
        )

        assert "created at" in result
        readme = tmp_content_root / "projects" / "my-tutorial" / "README.md"
        content = readme.read_text(encoding="utf-8")
        assert "# My Tutorial" in content
        assert "slug: my-tutorial" in content
        assert "type: tutorial" in content
        assert "{{title}}" not in content

    def test_returns_actionable_error_when_template_missing(
        self,
        patched_server: Any,
        tmp_content_root: Path,
    ) -> None:
        # No project.md written -> template file is missing
        result = patched_server.create_project_structure(
            title="Broken Project",
            video_type="tutorial",
        )

        assert "Template not found" in result
        assert "project.md" in result
        # Project directory must not have a README.md written from fallback
        readme = tmp_content_root / "projects" / "broken-project" / "README.md"
        assert not readme.exists()


class TestCreateEpisodeTemplate:
    def test_renders_template_when_file_present(
        self,
        patched_server: Any,
        tmp_plugin_root: Path,
        sample_project: Path,
    ) -> None:
        _write_template(
            tmp_plugin_root,
            "episode.md",
            "# {{title}}\nnumber: {{number}}\nslug: {{slug}}\n",
        )

        result = patched_server.create_episode(
            project_slug="test-tutorial",
            title="New Episode",
            number=2,
        )

        assert "created at" in result
        readme = sample_project / "episodes" / "02-new-episode" / "README.md"
        content = readme.read_text(encoding="utf-8")
        assert "# New Episode" in content
        assert "number: 2" in content
        assert "slug: 02-new-episode" in content
        assert "{{title}}" not in content

    def test_returns_actionable_error_when_template_missing(
        self,
        patched_server: Any,
        sample_project: Path,
    ) -> None:
        result = patched_server.create_episode(
            project_slug="test-tutorial",
            title="Broken Episode",
            number=9,
        )

        assert "Template not found" in result
        assert "episode.md" in result
        readme = sample_project / "episodes" / "09-broken-episode" / "README.md"
        assert not readme.exists()


class TestCreateSceneTemplate:
    def test_renders_template_when_file_present(
        self,
        patched_server: Any,
        tmp_plugin_root: Path,
        sample_episode: Path,
    ) -> None:
        _write_template(
            tmp_plugin_root,
            "scene.md",
            "# {{title}}\nnumber: {{number}}\nvisual: {{visual_type}}\n",
        )

        result = patched_server.create_scene(
            project_slug="test-tutorial",
            episode_slug="01-getting-started",
            title="New Scene",
            number=3,
            visual_type="slides",
        )

        assert "created at" in result
        scene_file = sample_episode / "scenes" / "03-new-scene.md"
        content = scene_file.read_text(encoding="utf-8")
        assert "# New Scene" in content
        assert "number: 3" in content
        assert "visual: slides" in content
        assert "{{title}}" not in content

    def test_returns_actionable_error_when_template_missing(
        self,
        patched_server: Any,
        sample_episode: Path,
    ) -> None:
        result = patched_server.create_scene(
            project_slug="test-tutorial",
            episode_slug="01-getting-started",
            title="Broken Scene",
            number=9,
        )

        assert "Template not found" in result
        assert "scene.md" in result
        scene_file = sample_episode / "scenes" / "09-broken-scene.md"
        assert not scene_file.exists()
