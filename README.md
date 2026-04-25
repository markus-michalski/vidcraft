# VidCraft

![GitHub Tag](https://img.shields.io/github/v/tag/markus-michalski/vidcraft?sort=semver&style=for-the-badge&logo=youtube)
![License: PolyForm NC 1.0.0](https://img.shields.io/badge/license-PolyForm%20NC%201.0.0-red.svg?style=for-the-badge)

AI Video Production Plugin for Claude Code. 33 specialized skills, dual-platform formatting (HeyGen & Synthesia), 12 video types, quality gates — from concept to published video.

**📖 Full documentation:** [faq.markus-michalski.net/en/plugins/vidcraft](https://faq.markus-michalski.net/en/plugins/vidcraft)

The documentation covers every skill in detail, the complete production pipeline, all video types, configuration, templates, and troubleshooting. Start there.

## Quick Start

```bash
# 1. Install the plugin
claude plugin add vidcraft

# 2. First-time setup
/vidcraft:setup

# 3. Create a new video project
/vidcraft:new-project

# 4. See all available commands
/vidcraft:help
```

## Requirements

- Claude Code CLI
- Python 3.10+
- HeyGen or Synthesia account (for video generation)
- Whisper (optional, for subtitle generation)

## Architecture

```
vidcraft/
├── skills/       # 33 specialized skills (SKILL.md files)
├── servers/      # FastMCP server (vidcraft-mcp)
├── tools/        # Python backend (state, parsers, indexer, format)
├── video-types/  # 12 video type definitions (tutorial, explainer, etc.)
├── knowledge/    # Script-writing rules, platform constraints
├── reference/    # Reference documentation
├── templates/    # Markdown scaffolds for projects/episodes/scenes
├── hooks/        # Validation hooks
└── tests/        # pytest suite
```

## Contributing

Contributions are welcome under a **Benevolent Dictator For Life (BDFL)** governance model. All PRs require signing the [CLA](CLA.md) (automated via [cla-assistant.io](https://cla-assistant.io/)).

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR. Bug reports and feature requests: use the [issue templates](https://github.com/markus-michalski/vidcraft/issues/new/choose). Security issues: [Private Vulnerability Reporting](https://github.com/markus-michalski/vidcraft/security/advisories/new).

## License

[PolyForm Noncommercial License 1.0.0](LICENSE.md) — source-available, personal and non-commercial use only. Not OSI Open Source. Commercial use requires explicit permission; contact the maintainer.
