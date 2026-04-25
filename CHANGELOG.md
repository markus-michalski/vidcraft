# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

### Changed
- migrate 10 opus skills from `claude-opus-4-6` to `claude-opus-4-7` (#24, phase 1)
- update test whitelist `valid_models` to accept `claude-opus-4-7`, drop `claude-opus-4-6`
- harden 9 opus skills against 4.7 default-shifts (#24, phase 2a):
  - script-writer: hard floor 80–150 words narration per scene
  - brief-creator: required depth per section (objective, audience, tone, etc.)
  - promo-writer: explicit length/hashtag floors per platform
  - storyboard-creator: no scene field may be left blank or "tbd"
  - video-reviewer: notes-column depth requirements per PASS/WARN/FAIL
  - audience-researcher: ≥3 parallel WebSearches + persona depth floor
  - researcher: ≥3 parallel WebSearches + ≥2 sources per finding + depth floor
  - doc-analyzer: ordered MCP tool execution (3+4+5 in parallel)
  - video-type-creator: ≥3 parallel WebSearches with distinct purposes

### Deprecated
- Nothing yet

### Removed
- Nothing yet

### Fixed
- Nothing yet

### Security
- Nothing yet

### Notes
- Phase 1 was frontmatter-only. Phase 2a addresses verbosity (Pattern A) and
  tool-use frequency (Pattern B) per the 4.7 migration guide.
- The multi-turn discovery refactor for `project-conceptualizer` (Pattern C)
  and the effort-level decision (Pattern D) follow in a separate PR — see
  #24 phase 2b.

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
