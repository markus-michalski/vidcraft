# VidCraft — AI Video Production Plugin

## Overview

VidCraft is a Claude Code plugin for creating professional AI-generated videos using HeyGen and Synthesia. It provides a structured workflow from concept to publication with specialized skills for each production phase.

## Skill Routing

When the user mentions or requests any of the following, route to the appropriate skill:

| User Intent | Skill |
|------------|-------|
| "Neues Projekt" / "New project" | `/vidcraft:new-project` IMMEDIATELY |
| Project name mentioned | `/vidcraft:resume [name]` |
| "Was kommt als nächstes?" / "What's next?" | `/vidcraft:next-step` |
| "Dashboard" / "Status" / "Fortschritt" | `/vidcraft:project-dashboard` |
| "Script schreiben" / "Write script" | `/vidcraft:script-writer` |
| "Script prüfen" / "Review script" | `/vidcraft:script-reviewer` |
| "Storyboard erstellen" | `/vidcraft:storyboard-creator` |
| "HeyGen" / "für HeyGen formatieren" | `/vidcraft:heygen-engineer` |
| "Synthesia" / "für Synthesia formatieren" | `/vidcraft:synthesia-engineer` |
| "Screenshots planen" / "Screenshot plan" | `/vidcraft:screenshot-planner` |
| "Assets prüfen" / "Check assets" | `/vidcraft:asset-collector` |
| "Shot list erstellen" | `/vidcraft:shot-list-creator` |
| "Avatar auswählen" / "Select avatar" | `/vidcraft:avatar-selector` |
| "Pre-gen check" / "Ready to generate?" | `/vidcraft:pre-generation-check` |
| "Neuer Video-Typ" / "New video type" | `/vidcraft:video-type-creator` |
| "Doku analysieren" / "Analyze docs" | `/vidcraft:doc-analyzer` |
| "Brief erstellen" / "Creative brief" | `/vidcraft:brief-creator` |
| "Konzept entwickeln" / "Plan the project" | `/vidcraft:project-conceptualizer` |
| "Recherche" / "Research" | `/vidcraft:researcher` |
| "Zielgruppe" / "Audience" | `/vidcraft:audience-researcher` |
| "Video reviewen" / "Review" | `/vidcraft:video-reviewer` |
| "Brand Check" / "Markencheck" | `/vidcraft:brand-checker` |
| "Barrierefreiheit" / "Accessibility" | `/vidcraft:accessibility-checker` |
| "AI Check" / "Voice Check" | `/vidcraft:voice-checker` |
| "Timing prüfen" | `/vidcraft:timing-validator` |
| "Release" / "Veröffentlichen" | `/vidcraft:release-director` |
| "Promo Text" / "Social Media" | `/vidcraft:promo-writer` |
| "Untertitel" / "Subtitles" / "Whisper" / "SRT" | `/vidcraft:subtitle-generator` |
| "Thumbnail" | `/vidcraft:thumbnail-director` |
| "Hilfe" / "Help" / "Was kann ich?" | `/vidcraft:help` |
| "Setup" / "Einrichten" | `/vidcraft:setup` |
| "Config" / "Konfiguration" | `/vidcraft:configure` |

## Workflow Pipeline

```
Concept → Script → Review → Storyboard → Assets → Pre-Gen Check → Generate → Review → Subtitles → Publish
```

### Standard Workflow
1. `/vidcraft:new-project` — Create project structure
1b. `/vidcraft:doc-analyzer` — (Optional) Analyze existing documentation
1c. `/vidcraft:project-conceptualizer` — Develop concept and episode plan
1d. `/vidcraft:brief-creator` — Create creative brief
2. `/vidcraft:script-writer` — Write scripts per episode
3. `/vidcraft:script-reviewer` — QC with 14-point checklist
4. `/vidcraft:storyboard-creator` — Visual direction per scene
5. `/vidcraft:screenshot-planner` — Define required screenshots and recordings
5b. `/vidcraft:asset-collector` — Verify all assets are ready
5c. `/vidcraft:shot-list-creator` — Production-ready shot list
6. `/vidcraft:avatar-selector` — Choose avatar and voice
6b. `/vidcraft:pre-generation-check` — Quality gates
7. `/vidcraft:heygen-engineer` or `/vidcraft:synthesia-engineer` — Platform formatting
7. [Manual] Generate in HeyGen/Synthesia
8. [Manual] Post-production in Shotcut (Intro/Outro, Schnitte)
9. `/vidcraft:subtitle-generator` — Whisper SRT + English translation
10. Review and publish

## Project Structure

Projects live at `{content_root}/projects/{slug}/`:
```
{project-slug}/
├── README.md           # Project metadata (YAML frontmatter)
├── episodes/
│   └── {episode-slug}/
│       ├── README.md   # Episode metadata
│       ├── scenes/
│       │   ├── 01-intro.md
│       │   └── 02-step-1.md
│       └── assets/
├── assets/             # Project-wide assets
└── research/           # Source documentation
```

## Status Progressions

### Project
```
Concept → Brief Complete → Research Done → Script Draft → Script Approved
→ Storyboard Done → Assets Ready → Generated → Reviewed → Published
```

### Episode
```
Not Started → Script Draft → Script Reviewed → Storyboard
→ Assets Collected → Ready for Generation → Generated → QA Passed → Final
```

### Scene
```
Outline → Script Written → Visual Defined → Assets Ready → Generated → Approved
```

## MCP Server

The `vidcraft-mcp` server provides tools for:
- **State Management:** list/find/get projects, episodes, scenes
- **Content Operations:** create structures, update fields, resolve paths
- **Script Analysis:** timing, readability, structure validation
- **Quality Gates:** pre-generation checks, project structure validation
- **Ideas:** brainstorming and idea tracking

## Video Types

Each video type has specific conventions in `video-types/<type>/README.md`:
- **tutorial** — Step-by-step instructional (3-15 min)
- **installation-guide** — Software installation walkthrough (2-8 min)
- **product-demo** — Feature showcase and benefits (2-5 min)
- **explainer** — Concept/product explanation (60-120s)
- **training** — Structured educational content (5-20 min)
- **onboarding** — Welcome and first steps (3-10 min)

More types can be created with `/vidcraft:video-type-creator`.

## Model Strategy

Each skill declares its model in YAML frontmatter (single source of truth). When creating new skills, choose the model based on the task profile:

| Task Profile | Model | Rationale |
|--------------|-------|-----------|
| Creative writing (scripts, briefs, concepts) | Opus | Needs nuance, voice, natural language |
| Research & synthesis | Opus | Complex source analysis |
| Type creation (video-type, genre definitions) | Opus | Comprehensive creative definition |
| Reviews & validation (checklists, QC) | Sonnet | Structured analysis, consistent output |
| Platform formatting (HeyGen, Synthesia, YouTube) | Sonnet | Technical, rule-based |
| Project management (state, routing, status) | Sonnet | State reading, workflow orchestration |
| Quick lookups (help, timing checks) | Haiku | Fast, simple, informational |

### Effort Level

VidCraft skills do **not** pin an `effort` field in frontmatter. As of Claude 4.7
the platform default is `xhigh` (raised from `high` in 4.6). We accept this
default globally — the quality gain on long-form creative output (scripts,
briefs, concepts) outweighs the additional token spend for the projects this
plugin runs.

If a future skill needs to override (e.g. a high-volume batch utility where
quality matters less than throughput), pin `effort: high` explicitly in that
skill's frontmatter and document the reason in the skill body.

## Code Style

- Python code: English comments, type hints, PEP 8
- Markdown: English for reference docs, German or English for user content
- YAML frontmatter: always present in project/episode/scene files

## Important Rules

1. ALWAYS use MCP tools for state operations — never parse files directly in skills
2. ALWAYS load the video type README before writing scripts
3. NEVER skip the pre-generation check before generation
4. Scripts must follow the 14-point quality checklist
5. Scene files must have narration, on-screen text, AND visual direction
