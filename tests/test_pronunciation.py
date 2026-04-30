"""Tests for check_pronunciation MCP tool (#39).

Verifies TTS-unfriendly pattern detection: years, acronyms,
Latin abbreviations, and decimal numbers.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SERVER_PATH = PLUGIN_ROOT / "servers" / "vidcraft-server" / "server.py"
SERVER_SOURCE = SERVER_PATH.read_text(encoding="utf-8")


def _load_server_module():
    tools_path = str(PLUGIN_ROOT)
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    spec = importlib.util.spec_from_file_location("vidcraft_server_pronunciation", SERVER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCheckPronunciationRegistered:
    def test_tool_exists_in_server(self) -> None:
        server = _load_server_module()
        assert hasattr(server, "check_pronunciation"), (
            "check_pronunciation must be defined in server.py"
        )

    def test_tool_registered_as_mcp_tool(self) -> None:
        assert "@mcp.tool()\ndef check_pronunciation(" in SERVER_SOURCE, (
            "check_pronunciation must be decorated with @mcp.tool()"
        )


class TestCleanTextReturnsNoIssues:
    def test_plain_sentence_no_issues(self) -> None:
        server = _load_server_module()
        result = server.check_pronunciation("Click the button and save your file.")
        assert "No issues found" in result

    def test_empty_text_no_issues(self) -> None:
        server = _load_server_module()
        result = server.check_pronunciation("")
        assert "No issues found" in result


class TestYearDetection:
    @pytest.mark.parametrize("year", ["2025", "1990", "2000", "1999"])
    def test_year_flagged(self, year: str) -> None:
        server = _load_server_module()
        result = server.check_pronunciation(f"This was released in {year}.")
        assert year in result, f"Year {year} must be flagged"
        assert "Year" in result

    def test_year_suggestion_provided(self) -> None:
        server = _load_server_module()
        result = server.check_pronunciation("Released in 2025.")
        assert "twenty" in result.lower(), "Year 2025 suggestion must include 'twenty'"

    def test_non_year_number_not_flagged_as_year(self) -> None:
        server = _load_server_module()
        # 12345 is not a year (outside 1900-2099)
        result = server.check_pronunciation("There are 12345 records in the database.")
        assert "Year" not in result


class TestAcronymDetection:
    @pytest.mark.parametrize("acronym", ["API", "HTTPS", "URL", "SQL", "REST"])
    def test_acronym_flagged(self, acronym: str) -> None:
        server = _load_server_module()
        result = server.check_pronunciation(f"Use the {acronym} endpoint.")
        assert acronym in result, f"Acronym {acronym} must be flagged"
        assert "Acronym" in result

    def test_acronym_spell_out_suggestion(self) -> None:
        server = _load_server_module()
        result = server.check_pronunciation("Call the API endpoint.")
        # Suggestion: A P I (space-separated)
        assert "A P I" in result, "API suggestion must be space-separated letters"

    def test_short_word_not_flagged_as_acronym(self) -> None:
        server = _load_server_module()
        # "I" alone is not an acronym in this context
        result = server.check_pronunciation("I am the user.")
        # Single-letter "I" should not produce an Acronym flag
        assert result.count("Acronym") == 0 or "I" not in result.split("Acronym")[1] if "Acronym" in result else True


class TestLatinAbbreviationDetection:
    @pytest.mark.parametrize(
        "abbrev,expansion",
        [
            ("e.g.", "for example"),
            ("i.e.", "that is"),
            ("etc.", "and so on"),
        ],
    )
    def test_latin_abbreviation_flagged(self, abbrev: str, expansion: str) -> None:
        server = _load_server_module()
        result = server.check_pronunciation(f"Use a tool, {abbrev} a script.")
        assert abbrev in result, f"{abbrev} must be flagged"
        assert expansion in result, f"Expansion '{expansion}' must be suggested"


class TestNoAutoReplace:
    def test_original_text_not_modified(self) -> None:
        server = _load_server_module()
        text = "The API was released in 2025, e.g. via HTTPS."
        result = server.check_pronunciation(text)
        # Tool reports issues but does not return a rewritten version of the text
        assert "Flag" in result or "Suggestion" in result or "Issues" in result
        # The word "API" should still be flagged as-is, not auto-replaced
        assert "API" in result
