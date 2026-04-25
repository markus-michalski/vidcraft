# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- inline Model Strategy guideline table in CLAUDE.md (#4)
- Model Strategy reference in video-type-creator skill (#4)
- `knowledge/script-writing-rules.md` — narration rules, pause syntax, on-screen text rules, post-production overlay markers (#8)
- `knowledge/platform-checklist.md` — HeyGen and Synthesia constraints (backgrounds, character limits, pause support, layouts) (#8)
- `LICENSE.md` (PolyForm Noncommercial 1.0.0) — replaces previous MIT license (#15)
- `CLA.md` — Apache ICLA v2.2 adapted for PolyForm NC, signed via cla-assistant.io (#15)
- `CONTRIBUTING.md` rewrite — BDFL governance model, single-branch workflow, CLA gate, release process (#15)
- `.github/CODEOWNERS` — maintainer review required on all paths (#15)
- `.github/SECURITY.md` — private vulnerability reporting, AI-dev safeguards, secret-handling policy (#15)
- `.github/dependabot.yml` — weekly pip + GitHub Actions updates targeted at `main` (#15)
- `.github/pull_request_template.md` — CLA gate + release checklist (#15)
- `.github/ISSUE_TEMPLATE/` — bug, feature, config (blank issues disabled, docs link, security advisory link) (#15)
- README license badge + landing-page rewrite that delegates full documentation to the wiki (#15)

### Changed
- consolidate avatar selection criteria — `heygen-engineer` references `avatar-selector` as single source of truth; full table (5 categories, age range) lives only in `avatar-selector` (#6)
- `script-writer`, `heygen-engineer`, `synthesia-engineer`, `storyboard-creator` reference `knowledge/script-writing-rules.md` and `knowledge/platform-checklist.md` instead of duplicating narration rules and platform constraints (#8)
- **License**: MIT → PolyForm Noncommercial 1.0.0. Source-available but non-OSI. Commercial use now requires explicit permission from the maintainer. Existing clones under MIT keep their MIT rights for that snapshot; new clones fall under PolyForm NC. (#15)
- `.claude-plugin/plugin.json` license field now references `LICENSE.md` (#15)
- README reduced to landing-page scope; full per-skill / per-video-type documentation lives at https://faq.markus-michalski.net/en/plugins/vidcraft (#15)

### Deprecated
- Nothing yet

### Removed
- reference/model-strategy.md (drift-prone, unreferenced, 15 of 33 skills listed; YAML frontmatter remains single source of truth) (#4)
- `LICENSE` (MIT) — replaced by `LICENSE.md` (PolyForm NC) (#15)

### Fixed
- Nothing yet

### Security
- Private Vulnerability Reporting policy added (`.github/SECURITY.md`) (#15)
- Dependabot now opens grouped weekly PRs for pip + GitHub Actions updates (#15)

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
