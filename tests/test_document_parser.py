"""Tests for document analysis parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.analysis.document_parser import (
    DocumentSection,
    analyze_complexity,
    extract_key_points,
    parse_document,
    suggest_structure,
)


@pytest.fixture
def sample_markdown(tmp_path: Path) -> Path:
    """Create a sample markdown document."""
    doc = tmp_path / "test-doc.md"
    doc.write_text(
        """---
title: Gallery Module Documentation
---

# Gallery Module

## Overview

The Gallery Module adds image gallery functionality to your OXID eShop.
It supports drag-and-drop uploads, automatic image optimization, and
responsive gallery displays.

## Installation

1. Run composer require
2. Activate the module
3. Configure settings

```bash
composer require mmd/gallery
vendor/bin/oe-console module:activate mmd_gallery
```

## Configuration

Navigate to the admin panel and configure these settings:

- Gallery layout (grid or masonry)
- Image sizes (thumbnail, medium, large)
- Lightbox behavior

## Usage

After installation, the gallery is available on product detail pages.
Upload images via the admin panel or use the API.

```php
$gallery = oxNew(GalleryController::class);
$gallery->setImages($imageList);
```

## Troubleshooting

If images don't appear:
- Check file permissions
- Verify module is activated
- Clear the shop cache

""",
        encoding="utf-8",
    )
    return doc


@pytest.fixture
def short_markdown(tmp_path: Path) -> Path:
    """Create a short markdown document."""
    doc = tmp_path / "short.md"
    doc.write_text(
        """# Quick FAQ

## What is it?

A gallery module for OXID eShop.

## How to install?

Run composer require mmd/gallery.
""",
        encoding="utf-8",
    )
    return doc


class TestParseDocument:
    def test_parse_markdown(self, sample_markdown: Path) -> None:
        doc = parse_document(sample_markdown)
        assert doc.format == "markdown"
        assert doc.total_words > 50
        assert len(doc.sections) >= 4

    def test_sections_have_content(self, sample_markdown: Path) -> None:
        doc = parse_document(sample_markdown)
        overview = next((s for s in doc.sections if "Overview" in s.heading), None)
        assert overview is not None
        assert overview.word_count > 10

    def test_code_detection(self, sample_markdown: Path) -> None:
        doc = parse_document(sample_markdown)
        code_sections = [s for s in doc.sections if s.has_code]
        assert len(code_sections) >= 1

    def test_list_detection(self, sample_markdown: Path) -> None:
        doc = parse_document(sample_markdown)
        list_sections = [s for s in doc.sections if s.has_list]
        assert len(list_sections) >= 1

    def test_unsupported_format(self, tmp_path: Path) -> None:
        doc = tmp_path / "test.xyz"
        doc.write_text("content")
        with pytest.raises(ValueError, match="Unsupported format"):
            parse_document(doc)


class TestExtractKeyPoints:
    def test_extracts_points(self, sample_markdown: Path) -> None:
        doc = parse_document(sample_markdown)
        points = extract_key_points(doc)
        assert len(points) >= 3
        assert all("heading" in p for p in points)

    def test_max_points(self, sample_markdown: Path) -> None:
        doc = parse_document(sample_markdown)
        points = extract_key_points(doc, max_points=2)
        assert len(points) <= 2

    def test_code_flagged(self, sample_markdown: Path) -> None:
        doc = parse_document(sample_markdown)
        points = extract_key_points(doc)
        code_points = [p for p in points if p.get("type") == "code_demo"]
        assert len(code_points) >= 1


class TestSuggestStructure:
    def test_suggests_scenes(self, sample_markdown: Path) -> None:
        doc = parse_document(sample_markdown)
        structure = suggest_structure(doc)
        assert structure["scene_count"] >= 3
        assert "estimated_duration" in structure
        assert len(structure["scenes"]) >= 3

    def test_intro_and_closing(self, sample_markdown: Path) -> None:
        doc = parse_document(sample_markdown)
        structure = suggest_structure(doc)
        scenes = structure["scenes"]
        assert scenes[0]["title"] == "Introduction"
        assert scenes[-1]["title"] == "Summary & Next Steps"


class TestAnalyzeComplexity:
    def test_complex_doc(self, sample_markdown: Path) -> None:
        doc = parse_document(sample_markdown)
        result = analyze_complexity(doc)
        assert 0 <= result["complexity_score"] <= 100
        assert result["recommended_type"] in (
            "tutorial", "installation-guide", "product-demo", "explainer", "training"
        )
        assert result["recommended_episodes"] >= 1

    def test_short_doc(self, short_markdown: Path) -> None:
        doc = parse_document(short_markdown)
        result = analyze_complexity(doc)
        assert result["complexity_score"] < 50
        assert result["recommended_episodes"] == 1
