"""Tests for config loading and path resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.shared.config import (
    _deep_merge,
    _default_config,
    resolve_assets_path,
    resolve_project_path,
    resolve_video_path,
)
from tools.shared.paths import find_projects, slugify


class TestSlugify:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("My Tutorial", "my-tutorial"),
            ("OXID Gallery Module", "oxid-gallery-module"),
            ("  Spaces  Everywhere  ", "spaces-everywhere"),
            ("Special!@#Chars", "specialchars"),
            ("already-a-slug", "already-a-slug"),
            ("Über die Konfiguration", "über-die-konfiguration"),
        ],
    )
    def test_slugify(self, text: str, expected: str) -> None:
        assert slugify(text) == expected


class TestDeepMerge:
    def test_simple_merge(self) -> None:
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        _deep_merge(base, override)
        assert base == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self) -> None:
        base = {"paths": {"root": "/a", "cache": "/b"}}
        override = {"paths": {"root": "/c"}}
        _deep_merge(base, override)
        assert base["paths"]["root"] == "/c"
        assert base["paths"]["cache"] == "/b"

    def test_override_non_dict_with_dict(self) -> None:
        base = {"x": "string"}
        override = {"x": {"nested": True}}
        _deep_merge(base, override)
        assert base["x"] == {"nested": True}


class TestDefaultConfig:
    def test_has_required_keys(self) -> None:
        config = _default_config()
        assert "paths" in config
        assert "defaults" in config
        assert "content_root" in config["paths"]


class TestPathResolution:
    def test_resolve_project_path(self, mock_config: dict) -> None:
        path = resolve_project_path(mock_config, "my-tutorial")
        assert path.name == "my-tutorial"
        assert "projects" in str(path)

    def test_resolve_video_path(self, mock_config: dict) -> None:
        path = resolve_video_path(mock_config, "my-tutorial")
        assert "videos" in str(path)

    def test_resolve_assets_path(self, mock_config: dict) -> None:
        path = resolve_assets_path(mock_config, "my-tutorial")
        assert "assets" in str(path)


class TestFindProjects:
    def test_find_projects(self, sample_project: Path, mock_config: dict) -> None:
        projects = find_projects(mock_config)
        assert len(projects) == 1
        assert projects[0].name == "test-tutorial"

    def test_find_projects_empty(self, mock_config: dict) -> None:
        projects = find_projects(mock_config)
        assert projects == []
