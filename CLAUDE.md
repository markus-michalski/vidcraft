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
| "Pre-gen check" / "Ready to generate?" | `/vidcraft:pre-generation-check` |
| "Neuer Video-Typ" / "New video type" | `/vidcraft:video-type-creator` |
| "Doku analysieren" / "Analyze docs" | `/vidcraft:doc-analyzer` |
| "Brief erstellen" / "Creative brief" | `/vidcraft:brief-creator` |
| "Konzept entwickeln" / "Plan the project" | `/vidcraft:project-conceptualizer` |
| "Recherche" / "Research" | `/vidcraft:researcher` |
| "Zielgruppe" / "Audience" | `/vidcraft:audience-researcher` |
| "Hilfe" / "Help" / "Was kann ich?" | `/vidcraft:help` |
| "Setup" / "Einrichten" | `/vidcraft:setup` |
| "Config" / "Konfiguration" | `/vidcraft:configure` |

## Workflow Pipeline

```
Concept → Script → Review → Storyboard → Assets → Pre-Gen Check → Generate → Review → Publish
```

### Standard Workflow
1. `/vidcraft:new-project` — Create project structure
1b. `/vidcraft:doc-analyzer` — (Optional) Analyze existing documentation
1c. `/vidcraft:project-conceptualizer` — Develop concept and episode plan
1d. `/vidcraft:brief-creator` — Create creative brief
2. `/vidcraft:script-writer` — Write scripts per episode
3. `/vidcraft:script-reviewer` — QC with 14-point checklist
4. `/vidcraft:storyboard-creator` — Visual direction per scene
5. `/vidcraft:pre-generation-check` — Quality gates
6. `/vidcraft:heygen-engineer` or `/vidcraft:synthesia-engineer` — Platform formatting
7. [Manual] Generate in HeyGen/Synthesia
8. Review and publish

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
