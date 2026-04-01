"""Tests for plugin structure integrity — validates all required files exist."""

from __future__ import annotations

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
            "claude-opus-4-6",
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
