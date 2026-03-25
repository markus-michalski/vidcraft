---
name: help
description: "Show available skills, common workflows, and quick reference for VidCraft. Use when the user asks for help or what skills are available."
model: claude-haiku-4-5-20251001
user-invocable: true
allowed-tools:
  - Read
  - Glob
---

# VidCraft Help

Show the user available skills and common workflows.

## Output

```
# VidCraft — AI Video Production Plugin

## Core Commands
- `/vidcraft:new-project` — Create a new video project
- `/vidcraft:session-start` — Initialize session, check status
- `/vidcraft:resume [project]` — Continue working on a project
- `/vidcraft:next-step` — Get recommended next action
- `/vidcraft:project-dashboard [project]` — Show progress overview

## Writing
- `/vidcraft:script-writer [project] [episode]` — Write episode script
- `/vidcraft:script-reviewer [project] [episode]` — Review script (14-point QC)

## Visual
- `/vidcraft:storyboard-creator [project] [episode]` — Create storyboard

## Production
- `/vidcraft:heygen-engineer [project] [episode]` — Format for HeyGen
- `/vidcraft:synthesia-engineer [project] [episode]` — Format for Synthesia
- `/vidcraft:pre-generation-check [project] [episode]` — Pre-gen quality gates

## Utility
- `/vidcraft:video-type-creator [type-name]` — Create new video type
- `/vidcraft:configure` — Set up config
- `/vidcraft:setup` — First-time setup

## Typical Workflow
1. `/vidcraft:new-project` → Create project
2. Script writing → `/vidcraft:script-writer`
3. Script review → `/vidcraft:script-reviewer`
4. Storyboard → `/vidcraft:storyboard-creator`
5. Pre-gen check → `/vidcraft:pre-generation-check`
6. Platform format → `/vidcraft:heygen-engineer` or `synthesia-engineer`
7. Generate in HeyGen/Synthesia (manual)
8. Review and publish
```
