# VidCraft

AI Video Production Plugin for [Claude Code](https://claude.com/claude-code) — Create professional videos with HeyGen & Synthesia.

## What it does

VidCraft guides you through the entire video production pipeline:

**Concept** → **Script** → **Review** → **Storyboard** → **Assets** → **Generate** → **Publish**

It provides specialized AI agents for each phase, quality gates before generation, and platform-specific formatting for HeyGen and Synthesia.

## Features

- **15 specialized skills** for script writing, storyboarding, platform engineering, and more
- **22 MCP tools** for project management, script analysis, quality gates, and ideas
- **3 video types** out of the box: Tutorial, Installation Guide, Product Demo
- **On-demand type creation** — create new video types with `/vidcraft:video-type-creator`
- **14-point script quality checklist** with automated checks
- **Pre-generation gates** that block until content is ready
- **Dual platform support** — HeyGen and Synthesia formatting from day one

## Installation

```bash
# Clone the repository
git clone https://github.com/markus-michalski/vidcraft.git

# Install as Claude Code plugin
claude plugin install ./vidcraft

# Run first-time setup
# In Claude Code:
/vidcraft:setup
```

## Quick Start

```
/vidcraft:new-project "OXID Gallery Tutorial" tutorial
/vidcraft:script-writer oxid-gallery-tutorial 01-installation
/vidcraft:script-reviewer oxid-gallery-tutorial 01-installation
/vidcraft:storyboard-creator oxid-gallery-tutorial 01-installation
/vidcraft:pre-generation-check oxid-gallery-tutorial 01-installation
/vidcraft:heygen-engineer oxid-gallery-tutorial 01-installation
```

## Skills

### Core
| Skill | Description |
|-------|-------------|
| `new-project` | Create a new video project with structure |
| `session-start` | Initialize session, verify setup |
| `resume` | Continue working on a project |
| `next-step` | Get recommended next action |
| `project-dashboard` | Show progress overview |

### Writing
| Skill | Description |
|-------|-------------|
| `script-writer` | Write scripts with narration + visual cues |
| `script-reviewer` | 14-point quality checklist review |

### Visual
| Skill | Description |
|-------|-------------|
| `storyboard-creator` | Scene-by-scene storyboard with visuals |

### Production
| Skill | Description |
|-------|-------------|
| `heygen-engineer` | Format for HeyGen generation |
| `synthesia-engineer` | Format for Synthesia generation |
| `pre-generation-check` | Quality gates before generation |

### Utility
| Skill | Description |
|-------|-------------|
| `video-type-creator` | Create new video type definitions |
| `help` | Show available skills and workflows |
| `configure` | Set up configuration |
| `setup` | First-time setup |

## Video Types

| Type | Duration | Use Case |
|------|----------|----------|
| **tutorial** | 3-15 min | Step-by-step software instructions |
| **installation-guide** | 2-8 min | Software/plugin installation |
| **product-demo** | 2-5 min | Feature showcase and benefits |

Create more with `/vidcraft:video-type-creator`.

## Project Structure

```
~/video-projects/projects/{slug}/
├── README.md              # Project metadata
├── episodes/
│   └── 01-getting-started/
│       ├── README.md      # Episode metadata
│       ├── scenes/
│       │   ├── 01-intro.md
│       │   └── 02-step-1.md
│       └── assets/
├── assets/
└── research/
```

## Configuration

Config lives at `~/.vidcraft/config.yaml`:

```yaml
paths:
  content_root: "~/video-projects"
  video_root: "~/video-projects/videos"
  assets_root: "~/video-projects/assets"
defaults:
  language: ["de", "en"]   # single or list for multi-language
  wpm: 140
  platform: "heygen"
```

## Requirements

- Python 3.10+
- Claude Code 1.0+

## License

MIT
