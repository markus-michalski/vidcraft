"""Tests for state indexer and cache."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


from tools.state.indexer import SCHEMA_VERSION, StateCache, _scan_projects, build_state


class TestScanProjects:
    def test_scan_with_project(self, sample_project: Path) -> None:
        projects_dir = sample_project.parent
        result = _scan_projects(projects_dir)
        assert "test-tutorial" in result
        proj = result["test-tutorial"]
        assert proj["title"] == "Test Tutorial"
        assert proj["video_type"] == "tutorial"
        assert proj["status"] == "Script Draft"

    def test_scan_with_episodes(self, sample_episode: Path) -> None:
        projects_dir = sample_episode.parent.parent.parent
        result = _scan_projects(projects_dir)
        proj = result["test-tutorial"]
        assert proj["episode_count"] == 1
        assert "01-getting-started" in proj["episodes_data"]

    def test_scan_episode_scenes(self, sample_episode: Path) -> None:
        projects_dir = sample_episode.parent.parent.parent
        result = _scan_projects(projects_dir)
        ep = result["test-tutorial"]["episodes_data"]["01-getting-started"]
        assert ep["scene_count"] == 2
        assert "01-intro" in ep["scenes"]
        assert "02-setup" in ep["scenes"]

    def test_scan_empty_dir(self, tmp_content_root: Path) -> None:
        projects_dir = tmp_content_root / "projects"
        result = _scan_projects(projects_dir)
        assert result == {}


class TestBuildState:
    def test_build_state(self, sample_project: Path, mock_config: dict) -> None:
        with patch("tools.state.indexer.load_config", return_value=mock_config):
            state = build_state()
        assert state["schema_version"] == SCHEMA_VERSION
        assert "projects" in state
        assert "session" in state
        assert "built_at" in state

    def test_state_has_session(self, mock_config: dict) -> None:
        with patch("tools.state.indexer.load_config", return_value=mock_config):
            state = build_state()
        session = state["session"]
        assert "last_project" in session
        assert "pending_actions" in session


class TestStateCache:
    def test_cache_returns_state(self, sample_project: Path, mock_config: dict) -> None:
        with patch("tools.state.indexer.load_config", return_value=mock_config):
            cache = StateCache()
            state = cache.get()
        assert "projects" in state

    def test_invalidate_forces_rebuild(self, mock_config: dict) -> None:
        with patch("tools.state.indexer.load_config", return_value=mock_config):
            cache = StateCache()
            state1 = cache.get()
            cache.invalidate()
            state2 = cache.get()
        # Both should be valid states
        assert "schema_version" in state1
        assert "schema_version" in state2
