"""Smoke test: all skill SKILL.md files are valid and consistent.

Checks required frontmatter fields, valid model IDs, no duplicate names,
and that user-invocable is explicitly declared on every skill.

If this fails, skills will be silently ignored or behave incorrectly.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PLUGIN_ROOT / "skills"

VALID_MODELS = frozenset(
    {
        "claude-opus-4-7",
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001",
    }
)

REQUIRED_FIELDS = ("name", "description", "user-invocable", "model")

_SKILL_FILES = sorted(SKILLS_DIR.glob("*/SKILL.md"))


def _parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---"), f"{path}: must start with YAML frontmatter"
    end = text.index("---", 3)
    return yaml.safe_load(text[3:end]) or {}


class TestSkillCount:
    def test_minimum_skill_count(self) -> None:
        assert len(_SKILL_FILES) >= 33, (
            f"Expected ≥33 skills, found {len(_SKILL_FILES)}"
        )

    def test_each_skill_dir_has_skill_md(self) -> None:
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir():
                assert (skill_dir / "SKILL.md").exists(), (
                    f"Skill directory '{skill_dir.name}' missing SKILL.md"
                )

    def test_skills_are_flat(self) -> None:
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir():
                subdirs = [d for d in skill_dir.iterdir() if d.is_dir()]
                assert not subdirs, (
                    f"Skill '{skill_dir.name}' contains subdirectories — "
                    f"skills must be flat: {[d.name for d in subdirs]}"
                )


class TestSkillFrontmatter:
    @pytest.mark.parametrize("skill_path", _SKILL_FILES, ids=lambda p: p.parent.name)
    def test_required_fields_present(self, skill_path: Path) -> None:
        meta = _parse_frontmatter(skill_path)
        missing = [f for f in REQUIRED_FIELDS if f not in meta]
        assert not missing, (
            f"{skill_path.parent.name}/SKILL.md missing fields: {missing}"
        )

    @pytest.mark.parametrize("skill_path", _SKILL_FILES, ids=lambda p: p.parent.name)
    def test_model_is_valid(self, skill_path: Path) -> None:
        meta = _parse_frontmatter(skill_path)
        model = meta.get("model", "")
        assert model in VALID_MODELS, (
            f"{skill_path.parent.name}/SKILL.md: invalid model '{model}'. "
            f"Valid models: {sorted(VALID_MODELS)}"
        )

    @pytest.mark.parametrize("skill_path", _SKILL_FILES, ids=lambda p: p.parent.name)
    def test_user_invocable_is_boolean(self, skill_path: Path) -> None:
        meta = _parse_frontmatter(skill_path)
        value = meta.get("user-invocable")
        assert isinstance(value, bool), (
            f"{skill_path.parent.name}/SKILL.md: 'user-invocable' must be "
            f"true or false (bool), got {type(value).__name__}: {value!r}"
        )

    @pytest.mark.parametrize("skill_path", _SKILL_FILES, ids=lambda p: p.parent.name)
    def test_name_matches_directory(self, skill_path: Path) -> None:
        meta = _parse_frontmatter(skill_path)
        dir_name = skill_path.parent.name
        skill_name = meta.get("name", "")
        assert skill_name == dir_name, (
            f"SKILL.md 'name: {skill_name}' does not match directory name '{dir_name}'"
        )


class TestSkillUniqueness:
    def test_no_duplicate_skill_names(self) -> None:
        names = []
        for skill_path in _SKILL_FILES:
            meta = _parse_frontmatter(skill_path)
            names.append(meta.get("name", ""))
        duplicates = [n for n in names if names.count(n) > 1]
        assert not duplicates, f"Duplicate skill names: {sorted(set(duplicates))}"
