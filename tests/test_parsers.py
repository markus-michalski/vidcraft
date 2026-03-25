"""Tests for markdown/YAML frontmatter parsers."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.state.parsers import (
    _normalize_status,
    parse_episode_readme,
    parse_frontmatter,
    parse_project_readme,
    parse_scene_file,
)


class TestParseFrontmatter:
    def test_valid_frontmatter(self) -> None:
        text = "---\ntitle: Test\nstatus: Draft\n---\n\n# Body"
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "Test"
        assert meta["status"] == "Draft"
        assert "# Body" in body

    def test_no_frontmatter(self) -> None:
        text = "# Just a heading\n\nSome content."
        meta, body = parse_frontmatter(text)
        assert meta == {}
        assert body == text

    def test_invalid_yaml(self) -> None:
        text = "---\n: invalid: yaml: [broken\n---\n\nBody"
        meta, body = parse_frontmatter(text)
        assert meta == {}

    def test_empty_frontmatter(self) -> None:
        text = "---\n\n---\n\nBody"
        meta, body = parse_frontmatter(text)
        assert meta == {}
        assert "Body" in body


class TestNormalizeStatus:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("concept", "Concept"),
            ("Concept", "Concept"),
            ("CONCEPT", "Concept"),
            ("script draft", "Script Draft"),
            ("draft", "Script Draft"),
            ("not started", "Not Started"),
            ("", "Not Started"),
            ("Custom Status", "Custom Status"),
        ],
    )
    def test_normalization(self, raw: str, expected: str) -> None:
        assert _normalize_status(raw) == expected


class TestParseProjectReadme:
    def test_parse_sample_project(self, sample_project: Path) -> None:
        readme = sample_project / "README.md"
        result = parse_project_readme(readme)
        assert result["slug"] == "test-tutorial"
        assert result["title"] == "Test Tutorial"
        assert result["video_type"] == "tutorial"
        assert result["status"] == "Script Draft"
        assert result["platform"] == "heygen"
        assert result["language"] == "de"


class TestParseEpisodeReadme:
    def test_parse_sample_episode(self, sample_episode: Path) -> None:
        readme = sample_episode / "README.md"
        result = parse_episode_readme(readme)
        assert result["slug"] == "01-getting-started"
        assert result["title"] == "Getting Started"
        assert result["number"] == 1
        assert result["status"] == "Script Draft"


class TestParseSceneFile:
    def test_parse_scene(self, sample_episode: Path) -> None:
        scene = sample_episode / "scenes" / "01-intro.md"
        result = parse_scene_file(scene)
        assert result["title"] == "Introduction"
        assert result["number"] == 1
        assert result["status"] == "Script Written"
        assert result["visual_type"] == "avatar"
        assert "Welcome" in result["narration"]
        assert "Getting Started" in result["on_screen_text"]
        assert "Avatar center" in result["visual_direction"]

    def test_parse_screencast_scene(self, sample_episode: Path) -> None:
        scene = sample_episode / "scenes" / "02-setup.md"
        result = parse_scene_file(scene)
        assert result["visual_type"] == "screencast"
        assert "terminal" in result["narration"].lower()
