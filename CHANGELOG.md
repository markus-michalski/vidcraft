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
