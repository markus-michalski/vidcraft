# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

### Deprecated
- Nothing yet

### Removed
- Nothing yet

### Fixed
- Nothing yet

### Security
- Nothing yet

## [1.3.2] - 2026-05-27

### Added
- Phase 3 — Polish & Extended Platform Intelligence (#33 #36 #38 #39) (#44)
- platform feature parity — SSML, gestures, Express-2, Voice Director, Avatar IV (#42)

### Changed
- add server.py size gate — warn at 2000 lines (#65)
- hygiene bundle — hooks/ in ruff, stderr for hook output (#62)
- reduce heygen_format_script complexity to ~5 branches (#64)
- move lazy imports to top-level in server.py (#63)
- add mypy to venv and CI (#61)
- bump pypdf from 6.11.0 to 6.12.1 in the pip-all group (#60)
- bump the pip-all group with 2 updates (#59)
- raise server.py coverage 43% → 75%, add coverage gate (#58)
- add tests/smoke/ — 4 mandatory smoke tests (#57)
- correct effort-level default — high not xhigh

### Fixed
- sync venv and add requirements-dev.txt with pip-audit (#55)
- add coverage and HTML coverage directories to .gitignore
- correct platform limits and HeyGen pause caveat (#41)

### Security
- validate file_path params against content_root (#56)

## [1.3.1] - 2026-04-26

### Changed
- refactor(mcp)!: rename create_idea/get_ideas to create_video_idea/get_video_ideas

## [1.3.0] - 2026-04-25

### Changed
- batched discovery for project-conceptualizer + effort-level doc (#24) (#27)
- harden 9 opus skills for 4.7 default-shifts (#24) (#26)
- migrate opus model pin claude-opus-4-6 to claude-opus-4-7 (#24) (#25)

## [1.2.0] - 2026-04-25

### Added
- add Facebook + Instagram to promo-writer, default all platforms (#722070)

### Changed
- bump the pip-all group with 6 updates (#22)
- bump the actions-all group with 2 updates (#21)
- update validate-structure to check LICENSE.md
- reduce README to landing-page scope, document governance migration
- add governance hardening (PolyForm NC license + CLA + templates)
- add MCP tool layer integration tests (#9)
- extract script-writing rules and platform constraints to knowledge/ (#8)
- consolidate status-to-next-skill matrix (#7)
- consolidate duplicated avatar selection criteria (#6)
- extract AI language patterns to knowledge/ (#5)
- remove model-strategy.md, inline guideline in CLAUDE.md (#4)
- apply ruff format to server.py
- remove dead-code default templates from server.py (#3)

### Fixed
- consolidate format tools into platform-specific variants (#2)
- read plugin version dynamically from plugin.json (#1)

## [1.1.0] - 2026-04-01

### Added
- enforce youtube-nocookie.com for all embed codes (#307610)
- integrate HeyGen limitations into production skills (#807575)
- add subtitle-generator skill with Whisper workflow (#808689)
- add YouTube category recommendation to promo-writer skill (#498268)

### Changed
- add CONTRIBUTING.md with development setup and guidelines
- add GitHub Actions CI with lint, tests, and structure validation

### Fixed
- use runpy.run_path() instead of exec() to fix NameError in MCP tools

## [1.0.1] - 2026-03-29

### Fixed
- flatten skills directory structure for plugin system compatibility

## [1.0.0] - 2026-03-27

### Added
- multi-language support in config
- Phase 4 — Review, Distribution, Polish
- Phase 3 — Production Pipeline
- Phase 2 — Content Intelligence
- initial vidcraft plugin structure (MVP)

### Fixed
- add missing [Unreleased] comparison link to CHANGELOG.md
- remove unsupported version param from FastMCP constructor
- plugin.json schema — author as object, skills/mcpServers as paths
- marketplace.json schema — add required owner and plugins fields

[1.0.0]: https://github.com/markus-michalski/vidcraft/releases/tag/v1.0.0
[1.0.1]: https://github.com/markus-michalski/vidcraft/releases/tag/v1.0.1
[1.1.0]: https://github.com/markus-michalski/vidcraft/releases/tag/v1.1.0
[1.2.0]: https://github.com/markus-michalski/vidcraft/releases/tag/v1.2.0
[1.3.0]: https://github.com/markus-michalski/vidcraft/releases/tag/v1.3.0
[1.3.1]: https://github.com/markus-michalski/vidcraft/releases/tag/v1.3.1
[1.3.2]: https://github.com/markus-michalski/vidcraft/releases/tag/v1.3.2
