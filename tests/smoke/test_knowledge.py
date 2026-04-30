"""Smoke test: knowledge/ and reference/ files are parseable and non-empty.

Verifies the knowledge base that skills depend on is intact. A missing or
corrupted knowledge file silently breaks skill behaviour.
"""

from __future__ import annotations

from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = PLUGIN_ROOT / "knowledge"
REFERENCE_DIR = PLUGIN_ROOT / "reference"

_KNOWLEDGE_FILES = sorted(KNOWLEDGE_DIR.rglob("*.md"))
_REFERENCE_FILES = sorted(REFERENCE_DIR.rglob("*.md"))
_ALL_KNOWLEDGE = _KNOWLEDGE_FILES + _REFERENCE_FILES

REQUIRED_KNOWLEDGE_FILES = (
    "ai-language-patterns.md",
    "platform-checklist.md",
    "script-writing-rules.md",
    "status-workflow.md",
)

REQUIRED_REFERENCE_FILES = (
    "state-schema.md",
    "terminology.md",
)


class TestKnowledgeFilesExist:
    def test_knowledge_directory_exists(self) -> None:
        assert KNOWLEDGE_DIR.is_dir(), "knowledge/ directory missing"

    def test_reference_directory_exists(self) -> None:
        assert REFERENCE_DIR.is_dir(), "reference/ directory missing"

    @pytest.mark.parametrize("filename", REQUIRED_KNOWLEDGE_FILES)
    def test_required_knowledge_file_exists(self, filename: str) -> None:
        assert (KNOWLEDGE_DIR / filename).exists(), (
            f"Required knowledge file missing: knowledge/{filename}"
        )

    @pytest.mark.parametrize("filename", REQUIRED_REFERENCE_FILES)
    def test_required_reference_file_exists(self, filename: str) -> None:
        assert (REFERENCE_DIR / filename).exists(), (
            f"Required reference file missing: reference/{filename}"
        )


class TestKnowledgeFilesReadable:
    @pytest.mark.parametrize(
        "md_path", _ALL_KNOWLEDGE, ids=lambda p: str(p.relative_to(PLUGIN_ROOT))
    )
    def test_file_is_readable(self, md_path: Path) -> None:
        text = md_path.read_text(encoding="utf-8")
        assert len(text.strip()) > 0, f"{md_path.name} is empty"

    @pytest.mark.parametrize(
        "md_path", _ALL_KNOWLEDGE, ids=lambda p: str(p.relative_to(PLUGIN_ROOT))
    )
    def test_file_has_heading(self, md_path: Path) -> None:
        text = md_path.read_text(encoding="utf-8")
        assert any(line.startswith("#") for line in text.splitlines()), (
            f"{md_path.relative_to(PLUGIN_ROOT)}: no markdown heading found"
        )

    @pytest.mark.parametrize(
        "md_path", _ALL_KNOWLEDGE, ids=lambda p: str(p.relative_to(PLUGIN_ROOT))
    )
    def test_file_is_valid_utf8(self, md_path: Path) -> None:
        try:
            md_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            pytest.fail(f"{md_path.name}: UTF-8 decode error — {e}")


class TestSkillKnowledgeReferences:
    """Key skills must reference the canonical knowledge files."""

    @pytest.mark.parametrize(
        "skill_name",
        ["script-writer", "heygen-engineer", "storyboard-creator"],
    )
    def test_script_writing_rules_referenced(self, skill_name: str) -> None:
        skill_path = PLUGIN_ROOT / "skills" / skill_name / "SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        assert "knowledge/script-writing-rules.md" in text, (
            f"{skill_name}/SKILL.md must reference knowledge/script-writing-rules.md"
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
    def test_platform_checklist_referenced(self, skill_name: str) -> None:
        skill_path = PLUGIN_ROOT / "skills" / skill_name / "SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        assert "knowledge/platform-checklist.md" in text, (
            f"{skill_name}/SKILL.md must reference knowledge/platform-checklist.md"
        )
