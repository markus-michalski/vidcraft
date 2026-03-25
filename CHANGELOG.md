# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial plugin structure with `.claude-plugin/` manifest
- MCP server skeleton with FastMCP (stdio transport)
- Config system with `~/.vidcraft/config.yaml`
- State management with JSON cache and schema migrations
- Templates: project, episode, scene, script, storyboard
- Video types: tutorial, installation-guide, product-demo (MVP)
- Core skills: new-project, session-start, resume, next-step, project-dashboard
- Writing skills: script-writer, script-reviewer
- Visual skill: storyboard-creator
- Production skills: heygen-engineer, synthesia-engineer
- Utility skills: video-type-creator, help, configure, setup
- Reference system: HeyGen, Synthesia, video-craft knowledge base
