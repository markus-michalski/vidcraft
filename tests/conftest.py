"""Shared test fixtures for vidcraft tests."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def tmp_content_root(tmp_path: Path) -> Path:
    """Create a temporary content root with basic structure."""
    content = tmp_path / "content"
    content.mkdir()
    (content / "projects").mkdir()
    return content


@pytest.fixture
def sample_project(tmp_content_root: Path) -> Path:
    """Create a sample project with README."""
    project_dir = tmp_content_root / "projects" / "test-tutorial"
    project_dir.mkdir(parents=True)
    (project_dir / "episodes").mkdir()
    (project_dir / "assets").mkdir()

    readme = project_dir / "README.md"
    readme.write_text(
        """---
title: "Test Tutorial"
slug: "test-tutorial"
video_type: "tutorial"
status: "Script Draft"
platform: "heygen"
language: "de"
target_audience: "Developers"
description: "A test tutorial project"
created: "2026-03-25"
updated: "2026-03-25"
---

# Test Tutorial

## Overview

A test tutorial project for unit tests.

## Episodes

1. Getting Started

## Notes

""",
        encoding="utf-8",
    )
    return project_dir


@pytest.fixture
def sample_episode(sample_project: Path) -> Path:
    """Create a sample episode with scenes."""
    ep_dir = sample_project / "episodes" / "01-getting-started"
    ep_dir.mkdir(parents=True)
    (ep_dir / "scenes").mkdir()
    (ep_dir / "assets").mkdir()

    readme = ep_dir / "README.md"
    readme.write_text(
        """---
title: "Getting Started"
number: 1
slug: "01-getting-started"
status: "Script Draft"
duration_target: "5:00"
platform: "heygen"
description: "First steps with the product"
---

# Getting Started

## Description

First steps with the product.

## Scenes

1. Introduction
2. Setup

""",
        encoding="utf-8",
    )

    # Create two scenes
    scene1 = ep_dir / "scenes" / "01-intro.md"
    scene1.write_text(
        """---
title: "Introduction"
number: 1
status: "Script Written"
visual_type: "avatar"
duration: "0:15"
---

# Introduction

## Narration

Welcome to this tutorial. I will show you how to get started with the product in just a few minutes.

## On-Screen Text

Getting Started Guide

## Visual Direction

Avatar center, branded background, friendly wave gesture.

## Assets

Logo overlay top-left.

""",
        encoding="utf-8",
    )

    scene2 = ep_dir / "scenes" / "02-setup.md"
    scene2.write_text(
        """---
title: "Setup"
number: 2
status: "Script Written"
visual_type: "screencast"
duration: "0:45"
---

# Setup

## Narration

First, open your terminal and run the following command. This will install all required dependencies for your project.

## On-Screen Text

composer require mmd/gallery

## Visual Direction

Full-screen terminal, cursor on command line, show output after execution.

## Assets

Screen recording of terminal with composer install.

""",
        encoding="utf-8",
    )

    return ep_dir


@pytest.fixture
def mock_config(tmp_content_root: Path) -> dict[str, Any]:
    """Return a mock config pointing to the temp content root."""
    return {
        "paths": {
            "content_root": str(tmp_content_root),
            "video_root": str(tmp_content_root / "videos"),
            "assets_root": str(tmp_content_root / "assets"),
            "overrides": str(tmp_content_root / "overrides"),
        },
        "defaults": {
            "language": ["de"],
            "wpm": 140,
            "platform": "heygen",
        },
        "heygen": {"default_avatar": "", "default_voice": ""},
        "synthesia": {"default_avatar": "", "default_voice": ""},
        "brand": {"name": "Test Brand", "tone": ["friendly"]},
    }
