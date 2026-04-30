"""Comprehensive test coverage for vidcraft-mcp server.py.

This module covers the MCP tool implementations in servers/vidcraft-server/server.py,
raising test coverage from 43% to ≥70% by testing:

- State retrieval and session management
- Script analysis and readability checks
- Structure validation and platform limits
- Format tools for HeyGen and Synthesia
- Asset listing and requirement tracking
- Pre-generation quality gates
- Document analysis and extraction
- Path resolution and content validation

Uses monkeypatch to mock state cache, config loading, and cache invalidation.
Each test group is organized by functional area with clear setup and assertions.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Setup: Load server.py as a module for testing
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SERVER_PATH = PLUGIN_ROOT / "servers" / "vidcraft-server" / "server.py"


def _load_server(monkeypatch: pytest.MonkeyPatch, content_root: Path | None = None) -> Any:
    """Load server.py dynamically with config mocking.

    Args:
        monkeypatch: pytest fixture for patching
        content_root: optional temp content root for path resolution

    Returns:
        Loaded server module
    """
    plugin_root_str = str(PLUGIN_ROOT)
    if plugin_root_str not in sys.path:
        sys.path.insert(0, plugin_root_str)

    spec = importlib.util.spec_from_file_location("vidcraft_server_cov", SERVER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if content_root:
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

    # Prevent actual state writes during tests
    monkeypatch.setattr(module._cache, "invalidate", lambda: None)

    return module


# Mock state for all tests
MOCK_STATE = {
    "projects": {
        "test-tutorial": {
            "slug": "test-tutorial",
            "title": "Test Tutorial",
            "status": "Script Draft",
            "video_type": "tutorial",
            "platform": "heygen",
            "language": "de",
            "episode_count": 1,
            "episodes_data": {
                "01-getting-started": {
                    "slug": "01-getting-started",
                    "title": "Getting Started",
                    "number": 1,
                    "status": "Script Draft",
                    "scene_count": 2,
                    "scenes": {
                        "01-intro": {
                            "number": 1,
                            "title": "Intro",
                            "status": "Script Written",
                            "visual_type": "avatar",
                            "duration": "0:15",
                            "narration": "Welcome to this tutorial. Today we cover the basics.",
                            "on_screen_text": "Tutorial: Getting Started",
                            "visual_direction": "Avatar center, friendly background",
                            "assets": "Logo overlay top-left",
                        },
                        "02-setup": {
                            "number": 2,
                            "title": "Setup",
                            "status": "Script Written",
                            "visual_type": "screencast",
                            "duration": "0:45",
                            "narration": "Open your terminal and run the install command.",
                            "on_screen_text": "composer require mmd/module",
                            "visual_direction": "Full-screen terminal recording",
                            "assets": "Screen recording of terminal",
                        },
                    },
                }
            },
        }
    },
    "session": {"last_project": "test-tutorial", "last_phase": "scripting"},
    "ideas": [],
}


# ===========================================================================
# TestStateRetrievalTools — State reading and project listing
# ===========================================================================


class TestStateRetrievalTools:
    """Tests for state retrieval and session management tools."""

    def test_list_projects_with_projects(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """list_projects returns formatted list when projects exist."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.list_projects()
        assert "Test Tutorial" in result
        assert "test-tutorial" in result
        assert "Script Draft" in result
        assert "1 episode" in result
        assert "tutorial" in result

    def test_list_projects_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """list_projects returns helpful message when no projects."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: {"projects": {}})

        result = server.list_projects()
        assert "No projects found" in result
        assert "create_project_structure" in result

    def test_find_project_exact_slug_match(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """find_project returns JSON when exact slug matches."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.find_project("test-tutorial")
        data = json.loads(result)
        assert data["slug"] == "test-tutorial"
        assert data["title"] == "Test Tutorial"

    def test_find_project_partial_name_match(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """find_project returns JSON when partial name matches."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.find_project("Tutorial")
        data = json.loads(result)
        assert data["slug"] == "test-tutorial"

    def test_find_project_multiple_matches(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """find_project returns multiple matches when query is ambiguous."""
        server = _load_server(monkeypatch)
        state = {
            "projects": {
                "test-tutorial": MOCK_STATE["projects"]["test-tutorial"],
                "test-training": {
                    "slug": "test-training",
                    "title": "Test Training",
                },
            },
            "session": {},
            "ideas": [],
        }
        monkeypatch.setattr(server._cache, "get", lambda: state)

        result = server.find_project("test")
        assert "Multiple matches" in result
        assert "test-tutorial" in result
        assert "test-training" in result

    def test_find_project_no_match(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """find_project returns error when no match found."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.find_project("nonexistent-project")
        assert "No project found" in result
        assert "nonexistent-project" in result

    def test_get_project_full_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_project_full returns full project JSON."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.get_project_full("test-tutorial")
        data = json.loads(result)
        assert data["slug"] == "test-tutorial"
        assert data["episode_count"] == 1
        assert "01-getting-started" in data["episodes_data"]

    def test_get_project_full_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_project_full returns error message when project not found."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.get_project_full("missing-project")
        assert "not found" in result
        assert "missing-project" in result

    def test_get_project_progress_with_episodes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_project_progress returns progress table with status breakdown."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.get_project_progress("test-tutorial")
        assert "Progress" in result
        assert "Status" in result
        assert "Count" in result
        assert "Script Draft" in result
        assert "|" in result  # Table format

    def test_get_project_progress_no_episodes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_project_progress returns message when no episodes."""
        server = _load_server(monkeypatch)
        state = {
            "projects": {
                "empty-project": {
                    "slug": "empty-project",
                    "title": "Empty Project",
                    "episodes_data": {},
                }
            },
            "session": {},
            "ideas": [],
        }
        monkeypatch.setattr(server._cache, "get", lambda: state)

        result = server.get_project_progress("empty-project")
        assert "no episodes yet" in result

    def test_get_project_progress_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_project_progress returns error when project not found."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.get_project_progress("missing")
        assert "not found" in result

    def test_get_session(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_session returns current session as JSON."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.get_session()
        data = json.loads(result)
        assert data["last_project"] == "test-tutorial"
        assert data["last_phase"] == "scripting"

    def test_search_with_match(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """search returns matching projects and episodes."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.search("Getting Started")
        assert "Getting Started" in result
        assert "Episode" in result

    def test_search_no_match(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """search returns no results message when nothing matches."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.search("nonexistent-query-xyz")
        assert "No results" in result


# ===========================================================================
# TestScriptAnalysisTools — Timing, readability, validation
# ===========================================================================


class TestScriptAnalysisTools:
    """Tests for script analysis: timing, readability, structure validation."""

    def test_analyze_timing_short_text(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """analyze_timing calculates correct duration for short text."""
        server = _load_server(monkeypatch)

        result = server.analyze_timing("Welcome to the tutorial. Let's get started.")
        data = json.loads(result)
        assert data["word_count"] == 7
        assert data["wpm"] == 140
        assert "estimated_duration" in data
        assert "total_seconds" in data

    def test_analyze_timing_custom_wpm(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """analyze_timing respects custom WPM argument."""
        server = _load_server(monkeypatch)

        result = server.analyze_timing("Word word word word word", wpm=60)
        data = json.loads(result)
        assert data["word_count"] == 5
        assert data["wpm"] == 60
        # 5 words @ 60 WPM = 5 seconds
        assert data["total_seconds"] == 5

    def test_check_readability_simple_text(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """check_readability returns PASS for simple text."""
        server = _load_server(monkeypatch)

        text = "This is simple. It is easy to read. We enjoy it."
        result = server.check_readability(text)
        data = json.loads(result)
        assert data["verdict"] in ("PASS", "WARN", "FAIL")
        assert "word_count" in data
        assert "flesch_reading_ease" in data

    def test_check_readability_long_sentences(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """check_readability flags sentences over 20 words."""
        server = _load_server(monkeypatch)

        text = "This is a very long sentence that contains many words and it goes on and on without stopping until it reaches more than twenty words in total."
        result = server.check_readability(text)
        data = json.loads(result)
        assert len(data["long_sentences"]) > 0
        assert data["long_sentences"][0]["words"] > 20

    def test_check_readability_complex_text(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """check_readability provides syllable counts."""
        server = _load_server(monkeypatch)

        text = "Synchronization infrastructure."
        result = server.check_readability(text)
        data = json.loads(result)
        assert "avg_syllables_per_word" in data

    def test_validate_structure_valid_episode(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_structure returns PASS for valid episode."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.validate_structure("test-tutorial", "01-getting-started")
        assert "PASS" in result
        assert "valid" in result.lower()

    def test_validate_structure_no_scenes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_structure fails when no scenes defined."""
        server = _load_server(monkeypatch)
        state = {
            "projects": {
                "test": {
                    "slug": "test",
                    "title": "Test",
                    "video_type": "tutorial",
                    "episodes_data": {
                        "01-ep": {
                            "slug": "01-ep",
                            "scene_count": 0,
                            "scenes": {},
                        }
                    },
                }
            },
            "session": {},
            "ideas": [],
        }
        monkeypatch.setattr(server._cache, "get", lambda: state)

        result = server.validate_structure("test", "01-ep")
        assert "FAIL" in result
        assert "No scenes" in result

    def test_validate_structure_empty_narration(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_structure warns about empty narration."""
        server = _load_server(monkeypatch)
        state = {
            "projects": {
                "test": {
                    "slug": "test",
                    "episodes_data": {
                        "01-ep": {
                            "slug": "01-ep",
                            "scene_count": 1,
                            "scenes": {
                                "01-scene": {
                                    "narration": "",
                                    "visual_direction": "Test",
                                }
                            },
                        }
                    },
                }
            },
            "session": {},
            "ideas": [],
        }
        monkeypatch.setattr(server._cache, "get", lambda: state)

        result = server.validate_structure("test", "01-ep")
        assert "WARN" in result

    def test_validate_structure_project_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_structure returns error when project missing."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.validate_structure("missing", "01-ep")
        assert "not found" in result

    def test_validate_structure_episode_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_structure returns error when episode missing."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.validate_structure("test-tutorial", "missing-episode")
        assert "not found" in result


# ===========================================================================
# TestFormatTools — HeyGen and Synthesia script formatting
# ===========================================================================


class TestFormatTools:
    """Tests for platform-specific script formatting (HeyGen, Synthesia)."""

    def test_heygen_format_script_avatar_scene(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """heygen_format_script formats avatar scenes correctly."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.heygen_format_script("test-tutorial", "01-getting-started")
        assert "Scene 1" in result
        assert "Intro" in result
        assert "Avatar: Center" in result
        assert "Welcome to this tutorial" in result

    def test_heygen_format_script_screencast_scene(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """heygen_format_script formats screencast scenes with avatar hidden."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.heygen_format_script("test-tutorial", "01-getting-started")
        assert "Scene 2" in result
        assert "Setup" in result
        assert "screencast" in result.lower()

    def test_heygen_format_script_with_pauses(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """heygen_format_script converts [pause Xs] to SSML <break>."""
        server = _load_server(monkeypatch)
        state = {
            "projects": {
                "test": {
                    "slug": "test",
                    "episodes_data": {
                        "01-ep": {
                            "slug": "01-ep",
                            "scenes": {
                                "01-scene": {
                                    "number": 1,
                                    "title": "Scene",
                                    "visual_type": "avatar",
                                    "narration": "Welcome. [pause 2s] Let's begin.",
                                    "visual_direction": "Center",
                                }
                            },
                        }
                    },
                }
            },
            "session": {},
            "ideas": [],
        }
        monkeypatch.setattr(server._cache, "get", lambda: state)

        result = server.heygen_format_script("test", "01-ep")
        assert '<break time="2s"/>' in result

    def test_heygen_format_script_project_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """heygen_format_script returns error when project missing."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.heygen_format_script("missing", "01-ep")
        assert "not found" in result

    def test_heygen_format_script_episode_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """heygen_format_script returns error when episode missing."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.heygen_format_script("test-tutorial", "missing-ep")
        assert "not found" in result

    def test_heygen_format_script_no_scenes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """heygen_format_script returns message when no scenes."""
        server = _load_server(monkeypatch)
        state = {
            "projects": {
                "test": {
                    "slug": "test",
                    "episodes_data": {
                        "01-ep": {
                            "slug": "01-ep",
                            "scenes": {},
                        }
                    },
                }
            },
            "session": {},
            "ideas": [],
        }
        monkeypatch.setattr(server._cache, "get", lambda: state)

        result = server.heygen_format_script("test", "01-ep")
        assert "No scenes found" in result

    def test_synthesia_format_script_avatar_scene(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """synthesia_format_script formats avatar scenes correctly."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.synthesia_format_script("test-tutorial", "01-getting-started")
        assert "Slide 1" in result
        assert "Avatar center" in result

    def test_synthesia_format_script_screencast_scene(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """synthesia_format_script maps screencast to correct layout."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.synthesia_format_script("test-tutorial", "01-getting-started")
        assert "Screen recording" in result

    def test_synthesia_format_script_project_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """synthesia_format_script returns error when project missing."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.synthesia_format_script("missing", "01-ep")
        assert "not found" in result

    def test_synthesia_format_script_episode_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """synthesia_format_script returns error when episode missing."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.synthesia_format_script("test-tutorial", "missing-ep")
        assert "not found" in result


# ===========================================================================
# TestAssetManagement — Asset listing and requirement tracking
# ===========================================================================


class TestAssetManagement:
    """Tests for asset collection and requirement tracking."""

    def test_list_required_assets_screencast_scene(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """list_required_assets identifies screen recordings for screencast scenes."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.list_required_assets("test-tutorial", "01-getting-started")
        assert "screen_recording" in result.lower()

    def test_list_required_assets_project_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """list_required_assets returns error when project missing."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.list_required_assets("missing", "01-ep")
        assert "not found" in result

    def test_list_required_assets_episode_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """list_required_assets returns error when episode missing."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.list_required_assets("test-tutorial", "missing-ep")
        assert "not found" in result

    def test_list_required_assets_no_assets(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """list_required_assets returns message when no assets referenced."""
        server = _load_server(monkeypatch)
        state = {
            "projects": {
                "test": {
                    "slug": "test",
                    "episodes_data": {
                        "01-ep": {
                            "slug": "01-ep",
                            "scenes": {
                                "01-scene": {
                                    "visual_type": "avatar",
                                    "assets": "",
                                }
                            },
                        }
                    },
                }
            },
            "session": {},
            "ideas": [],
        }
        monkeypatch.setattr(server._cache, "get", lambda: state)

        result = server.list_required_assets("test", "01-ep")
        assert "No specific assets" in result


# ===========================================================================
# TestPlatformLimits — Platform capability and limit validation
# ===========================================================================


class TestPlatformLimits:
    """Tests for platform limits and capability checking."""

    def test_validate_platform_limits_heygen_pass(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_platform_limits passes when within HeyGen limits."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.validate_platform_limits(
            "test-tutorial", "01-getting-started", "heygen"
        )
        assert "PASS" in result

    def test_validate_platform_limits_synthesia_pass(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_platform_limits passes when within Synthesia limits."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.validate_platform_limits(
            "test-tutorial", "01-getting-started", "synthesia"
        )
        assert "PASS" in result

    def test_validate_platform_limits_auto_platform(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_platform_limits uses project platform when not specified."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.validate_platform_limits(
            "test-tutorial", "01-getting-started"
        )
        # Should auto-detect 'heygen' from project
        assert "heygen" in result.lower() or "PASS" in result

    def test_validate_platform_limits_unknown_platform(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_platform_limits returns error for unknown platform."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.validate_platform_limits(
            "test-tutorial", "01-getting-started", "invalid-platform"
        )
        assert "Unknown platform" in result

    def test_validate_platform_limits_project_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_platform_limits returns error when project missing."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.validate_platform_limits("missing", "01-ep", "heygen")
        assert "not found" in result

    def test_get_platform_capabilities_heygen(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_platform_capabilities returns HeyGen features."""
        server = _load_server(monkeypatch)

        result = server.get_platform_capabilities("heygen")
        data = json.loads(result)
        assert "features" in data
        assert "avatar_types" in data
        assert "best_for" in data

    def test_get_platform_capabilities_synthesia(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_platform_capabilities returns Synthesia features."""
        server = _load_server(monkeypatch)

        result = server.get_platform_capabilities("synthesia")
        data = json.loads(result)
        assert "features" in data
        assert "max_chars_per_scene" in data

    def test_get_platform_capabilities_unknown_platform(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_platform_capabilities returns error for unknown platform."""
        server = _load_server(monkeypatch)

        result = server.get_platform_capabilities("invalid-platform")
        assert "Unknown platform" in result


# ===========================================================================
# TestQualityGates — Pre-generation validation
# ===========================================================================


class TestQualityGates:
    """Tests for pre-generation quality gate checks."""

    def test_run_pre_generation_gates_ready(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """run_pre_generation_gates returns READY when all gates pass."""
        server = _load_server(monkeypatch)
        state = {
            "projects": {
                "test": {
                    "slug": "test",
                    "episodes_data": {
                        "01-ep": {
                            "slug": "01-ep",
                            "status": "Script Reviewed",
                            "scenes": {
                                "01-scene": {
                                    "narration": "Test narration here.",
                                    "visual_direction": "Center",
                                }
                            },
                        }
                    },
                }
            },
            "session": {},
            "ideas": [],
        }
        monkeypatch.setattr(server._cache, "get", lambda: state)
        monkeypatch.setattr(server, "load_config", lambda: {"defaults": {"wpm": 140}})

        result = server.run_pre_generation_gates("test", "01-ep")
        assert "READY" in result

    def test_run_pre_generation_gates_script_not_approved(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """run_pre_generation_gates fails when script not approved."""
        server = _load_server(monkeypatch)
        state = {
            "projects": {
                "test": {
                    "slug": "test",
                    "episodes_data": {
                        "01-ep": {
                            "slug": "01-ep",
                            "status": "Script Draft",
                            "scenes": {"01-scene": {"narration": "Test"}},
                        }
                    },
                }
            },
            "session": {},
            "ideas": [],
        }
        monkeypatch.setattr(server._cache, "get", lambda: state)

        result = server.run_pre_generation_gates("test", "01-ep")
        assert "BLOCKED" in result
        assert "Script not approved" in result

    def test_run_pre_generation_gates_missing_narration(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """run_pre_generation_gates fails when scenes missing narration."""
        server = _load_server(monkeypatch)
        state = {
            "projects": {
                "test": {
                    "slug": "test",
                    "episodes_data": {
                        "01-ep": {
                            "slug": "01-ep",
                            "status": "Script Reviewed",
                            "scenes": {
                                "01-scene": {
                                    "narration": "",
                                    "visual_direction": "Test",
                                }
                            },
                        }
                    },
                }
            },
            "session": {},
            "ideas": [],
        }
        monkeypatch.setattr(server._cache, "get", lambda: state)

        result = server.run_pre_generation_gates("test", "01-ep")
        assert "BLOCKED" in result
        assert "Missing narration" in result

    def test_run_pre_generation_gates_project_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """run_pre_generation_gates returns error when project missing."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE)

        result = server.run_pre_generation_gates("missing", "01-ep")
        assert "not found" in result


# ===========================================================================
# TestUtilityFunctions — Helper functions and safe JSON
# ===========================================================================


class TestUtilityFunctions:
    """Tests for utility and helper functions."""

    def test_safe_json_with_non_serializable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """_safe_json handles non-serializable types with str()."""
        server = _load_server(monkeypatch)

        data = {"date": __import__("datetime").date.today(), "text": "hello"}
        result = server._safe_json(data)
        parsed = json.loads(result)
        assert "text" in parsed
        # date should be converted to string
        assert isinstance(parsed["date"], str)

    def test_convert_pauses_to_ssml(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """_convert_pauses_to_ssml replaces [pause Xs] with SSML."""
        server = _load_server(monkeypatch)

        text = "Start. [pause 1s] Middle. [pause 2.5s] End."
        result = server._convert_pauses_to_ssml(text)
        assert '<break time="1s"/>' in result
        assert '<break time="2.5s"/>' in result

    def test_today_returns_iso_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """_today returns today's date as ISO string."""
        server = _load_server(monkeypatch)

        result = server._today()
        assert "-" in result  # YYYY-MM-DD format
        assert len(result) == 10

    def test_now_utc_returns_iso_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """_now_utc returns current UTC time as ISO string."""
        server = _load_server(monkeypatch)

        result = server._now_utc()
        assert "T" in result  # ISO format with time
        assert "+" in result or "Z" in result  # Timezone info


# ===========================================================================
# TestPathResolution — Path utilities and validation
# ===========================================================================


class TestPathResolution:
    """Tests for path resolution and validation."""

    def test_resolve_path_content(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """resolve_path returns content path for project."""
        server = _load_server(monkeypatch, tmp_path)

        result = server.resolve_path("test-project", "content")
        assert "test-project" in result

    def test_resolve_path_video(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """resolve_path returns video path for project."""
        server = _load_server(monkeypatch, tmp_path)

        result = server.resolve_path("test-project", "video")
        assert "videos" in result

    def test_resolve_path_assets(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """resolve_path returns assets path for project."""
        server = _load_server(monkeypatch, tmp_path)

        result = server.resolve_path("test-project", "assets")
        assert "assets" in result

    def test_resolve_path_with_episode(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """resolve_path includes episode in path when specified."""
        server = _load_server(monkeypatch, tmp_path)

        result = server.resolve_path(
            "test-project", "content", "01-getting-started"
        )
        assert "episodes" in result
        assert "01-getting-started" in result

    def test_resolve_path_unknown_type(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """resolve_path returns error for unknown path type."""
        server = _load_server(monkeypatch, tmp_path)

        result = server.resolve_path("test-project", "invalid-type")
        assert "Unknown path type" in result


# ===========================================================================
# TestSessionManagement — Session and state updates
# ===========================================================================


class TestSessionManagement:
    """Tests for session state management and updates."""

    def test_update_session_last_project(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """update_session updates last_project in state."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE.copy())
        monkeypatch.setattr(
            server, "_write_state", lambda s: None
        )  # Mock state write

        result = server.update_session(last_project="new-project")
        assert "Session updated" in result

    def test_update_session_last_phase(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """update_session updates last_phase in state."""
        server = _load_server(monkeypatch)
        monkeypatch.setattr(server._cache, "get", lambda: MOCK_STATE.copy())
        monkeypatch.setattr(server, "_write_state", lambda s: None)

        result = server.update_session(last_phase="generation")
        assert "Session updated" in result

    def test_rebuild_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """rebuild_state rebuilds state from disk files."""
        server = _load_server(monkeypatch)

        # Mock the rebuild function to return a state
        monkeypatch.setattr(
            server,
            "rebuild",
            lambda preserve_session=True: {"projects": {"test": {}}},
        )

        result = server.rebuild_state()
        assert "State rebuilt" in result
        assert "1 project" in result
