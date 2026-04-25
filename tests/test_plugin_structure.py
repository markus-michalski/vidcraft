"""Tests for plugin structure integrity — validates all required files exist."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

PLUGIN_ROOT = Path(__file__).resolve().parent.parent


class TestPluginManifest:
    def test_plugin_json_exists(self) -> None:
        assert (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").exists()

    def test_marketplace_json_exists(self) -> None:
        assert (PLUGIN_ROOT / ".claude-plugin" / "marketplace.json").exists()

    def test_mcp_json_exists(self) -> None:
        assert (PLUGIN_ROOT / ".mcp.json").exists()

    def test_claude_md_exists(self) -> None:
        assert (PLUGIN_ROOT / "CLAUDE.md").exists()

    def test_readme_exists(self) -> None:
        assert (PLUGIN_ROOT / "README.md").exists()


class TestSkillStructure:
    """Validate all skills have required SKILL.md with valid frontmatter."""

    def _get_all_skills(self) -> list[Path]:
        skills_dir = PLUGIN_ROOT / "skills"
        return sorted(skills_dir.rglob("SKILL.md"))

    def test_skills_exist(self) -> None:
        skills = self._get_all_skills()
        assert len(skills) >= 15, f"Expected 15+ skills, found {len(skills)}"

    @pytest.mark.parametrize(
        "skill_path", sorted((PLUGIN_ROOT / "skills").rglob("SKILL.md"))
    )
    def test_skill_has_frontmatter(self, skill_path: Path) -> None:
        text = skill_path.read_text(encoding="utf-8")
        assert text.startswith("---"), (
            f"{skill_path.name}: Must start with YAML frontmatter"
        )
        end = text.index("---", 3)
        meta = yaml.safe_load(text[3:end])
        assert "name" in meta, f"{skill_path}: Missing 'name' in frontmatter"
        assert "description" in meta, f"{skill_path}: Missing 'description'"
        assert "model" in meta, f"{skill_path}: Missing 'model'"

    @pytest.mark.parametrize(
        "skill_path", sorted((PLUGIN_ROOT / "skills").rglob("SKILL.md"))
    )
    def test_skill_model_valid(self, skill_path: Path) -> None:
        text = skill_path.read_text(encoding="utf-8")
        end = text.index("---", 3)
        meta = yaml.safe_load(text[3:end])
        valid_models = {
            "claude-opus-4-7",
            "claude-sonnet-4-6",
            "claude-haiku-4-5-20251001",
        }
        assert meta["model"] in valid_models, (
            f"{skill_path}: Invalid model '{meta['model']}'. Valid: {valid_models}"
        )


class TestVideoTypes:
    """Validate all video types have required README.md."""

    def test_mvp_types_exist(self) -> None:
        types_dir = PLUGIN_ROOT / "video-types"
        for vtype in ("tutorial", "installation-guide", "product-demo"):
            assert (types_dir / vtype / "README.md").exists(), (
                f"Missing: {vtype}/README.md"
            )

    def test_all_types_have_readme(self) -> None:
        types_dir = PLUGIN_ROOT / "video-types"
        for type_dir in sorted(types_dir.iterdir()):
            if type_dir.is_dir():
                assert (type_dir / "README.md").exists(), (
                    f"Missing README: {type_dir.name}"
                )

    def test_type_count(self) -> None:
        types_dir = PLUGIN_ROOT / "video-types"
        types = [
            d for d in types_dir.iterdir() if d.is_dir() and (d / "README.md").exists()
        ]
        assert len(types) >= 9, f"Expected 9+ video types, found {len(types)}"


class TestTemplates:
    """Validate all templates exist."""

    @pytest.mark.parametrize(
        "template",
        [
            "project.md",
            "episode.md",
            "scene.md",
            "script.md",
            "storyboard.md",
            "brief.md",
            "shot-list.md",
        ],
    )
    def test_template_exists(self, template: str) -> None:
        assert (PLUGIN_ROOT / "templates" / template).exists()


class TestServerFiles:
    def test_server_py_exists(self) -> None:
        assert (PLUGIN_ROOT / "servers" / "vidcraft-server" / "server.py").exists()

    def test_run_py_exists(self) -> None:
        assert (PLUGIN_ROOT / "servers" / "vidcraft-server" / "run.py").exists()


class TestToolModules:
    def test_config_module(self) -> None:
        assert (PLUGIN_ROOT / "tools" / "shared" / "config.py").exists()

    def test_paths_module(self) -> None:
        assert (PLUGIN_ROOT / "tools" / "shared" / "paths.py").exists()

    def test_indexer_module(self) -> None:
        assert (PLUGIN_ROOT / "tools" / "state" / "indexer.py").exists()

    def test_parsers_module(self) -> None:
        assert (PLUGIN_ROOT / "tools" / "state" / "parsers.py").exists()

    def test_document_parser_module(self) -> None:
        assert (PLUGIN_ROOT / "tools" / "analysis" / "document_parser.py").exists()


class TestKnowledgeFiles:
    """Validate knowledge/ Single-Source-of-Truth files and skill references.

    Issue #8: knowledge/ holds reusable plugin knowledge so duplicated
    constraints in skills can be replaced with references.
    """

    def test_script_writing_rules_exists(self) -> None:
        path = PLUGIN_ROOT / "knowledge" / "script-writing-rules.md"
        assert path.exists(), "knowledge/script-writing-rules.md must exist"

    def test_platform_checklist_exists(self) -> None:
        path = PLUGIN_ROOT / "knowledge" / "platform-checklist.md"
        assert path.exists(), "knowledge/platform-checklist.md must exist"

    @pytest.mark.parametrize(
        "skill_name",
        ["script-writer", "heygen-engineer", "storyboard-creator"],
    )
    def test_skill_references_script_writing_rules(self, skill_name: str) -> None:
        skill_path = PLUGIN_ROOT / "skills" / skill_name / "SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        assert "knowledge/script-writing-rules.md" in text, (
            f"{skill_name} must reference knowledge/script-writing-rules.md "
            f"instead of duplicating narration/pause/text-overlay rules."
        )

    @pytest.mark.parametrize(
        "skill_name",
        [
            "script-writer",
            "heygen-engineer",
            "synthesia-engineer",
            "storyboard-creator",
        ],
    )
    def test_skill_references_platform_checklist(self, skill_name: str) -> None:
        skill_path = PLUGIN_ROOT / "skills" / skill_name / "SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        assert "knowledge/platform-checklist.md" in text, (
            f"{skill_name} must reference knowledge/platform-checklist.md "
            f"instead of duplicating HeyGen/Synthesia constraints."
        )


class TestPluginVersion:
    """Single source of truth: plugin.json version must match get_plugin_version()."""

    def _load_server_module(self):
        # Ensure tools/ is importable (server.py requires it at import time)
        tools_path = str(PLUGIN_ROOT)
        if tools_path not in sys.path:
            sys.path.insert(0, tools_path)

        server_path = PLUGIN_ROOT / "servers" / "vidcraft-server" / "server.py"
        spec = importlib.util.spec_from_file_location(
            "vidcraft_server_under_test", server_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_plugin_json_has_version(self) -> None:
        plugin_json = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        data = json.loads(plugin_json.read_text(encoding="utf-8"))
        assert "version" in data, "plugin.json must declare a 'version' field"
        assert data["version"], "plugin.json 'version' must not be empty"

    def test_mcp_tool_returns_plugin_json_version(self) -> None:
        plugin_json = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        expected_version = json.loads(plugin_json.read_text(encoding="utf-8"))[
            "version"
        ]

        server = self._load_server_module()
        result = json.loads(server.get_plugin_version())

        assert result["version"] == expected_version, (
            f"get_plugin_version() returned '{result['version']}' but "
            f"plugin.json declares '{expected_version}'. Single source of "
            f"truth must be plugin.json."
        )
