#!/usr/bin/env python3
"""PostToolUse hook: Validate scene files after Write/Edit operations.

Checks that scene markdown files have required sections and valid frontmatter.
Runs automatically after any file write/edit that matches scene file patterns.
"""

import re
import sys
from pathlib import Path

import yaml


def validate_scene(file_path: str) -> list[str]:
    """Validate a scene file and return list of issues."""
    path = Path(file_path)
    issues: list[str] = []

    if not path.exists():
        return []

    # Only validate scene files (in scenes/ directories)
    if "/scenes/" not in str(path) or not path.suffix == ".md":
        return []

    text = path.read_text(encoding="utf-8")

    # Check frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not fm_match:
        issues.append(f"WARN: {path.name} — Missing YAML frontmatter")
    else:
        try:
            meta = yaml.safe_load(fm_match.group(1)) or {}
        except yaml.YAMLError:
            issues.append(f"FAIL: {path.name} — Invalid YAML frontmatter")
            return issues

        # Required frontmatter fields
        for field in ("title", "number", "status"):
            if field not in meta:
                issues.append(f"WARN: {path.name} — Missing frontmatter field: {field}")

    # Check required sections
    required_sections = ["Narration", "Visual Direction"]
    for section in required_sections:
        if f"## {section}" not in text:
            issues.append(f"WARN: {path.name} — Missing section: ## {section}")

    # Check narration is not just placeholder
    narration_match = re.search(
        r"## Narration\s*\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL
    )
    if narration_match:
        narration = narration_match.group(1).strip()
        if narration.startswith("*") and narration.endswith("*"):
            # Still placeholder text
            pass  # Don't warn — scene might be in Outline status
        elif len(narration.split()) > 0:
            # Check sentence length
            sentences = re.split(r"[.!?]+", narration)
            for sentence in sentences:
                words = sentence.strip().split()
                if len(words) > 25:
                    issues.append(
                        f"WARN: {path.name} — Long sentence ({len(words)} words): "
                        f'"{" ".join(words[:8])}..."'
                    )

    return issues


def main() -> None:
    """Run validation on the file passed as argument."""
    if len(sys.argv) < 2:
        return

    file_path = sys.argv[1]
    issues = validate_scene(file_path)

    if issues:
        for issue in issues:
            print(issue)
        # Exit 0 — hooks should warn, not block
        sys.exit(0)


if __name__ == "__main__":
    main()
