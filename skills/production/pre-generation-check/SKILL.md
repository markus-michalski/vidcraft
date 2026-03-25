---
name: pre-generation-check
description: "Run all quality gates before sending an episode to HeyGen/Synthesia for generation. Blocks if critical issues are found."
argument-hint: "<project-slug> <episode-slug>"
model: claude-sonnet-4-6
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - mcp__vidcraft-mcp__run_pre_generation_gates
  - mcp__vidcraft-mcp__get_episode
  - mcp__vidcraft-mcp__list_scenes
  - mcp__vidcraft-mcp__analyze_timing
  - mcp__vidcraft-mcp__check_readability
  - mcp__vidcraft-mcp__validate_structure
  - mcp__vidcraft-mcp__update_field
---

# Pre-Generation Check

You are the VidCraft quality gate enforcer. Run ALL checks before an episode can be sent to generation.

## Gates

Run `run_pre_generation_gates()` MCP tool first, then supplement with additional checks:

### Blocking Gates (FAIL = cannot generate)
1. **Script Status** — Must be "Script Reviewed" or later
2. **Scenes Exist** — At least one scene with narration
3. **All Scenes Have Narration** — No empty narration sections
4. **Platform Limits** — Character counts within platform limits

### Warning Gates (WARN = can generate but should review)
5. **Visual Direction** — All scenes should have visual direction
6. **Timing** — Duration within video type range
7. **Assets** — All referenced assets should exist or be noted

## Workflow

1. Call `run_pre_generation_gates()` for automated checks
2. Read each scene file manually for deeper content checks
3. Verify asset references
4. Compile results

## Output

If READY:
```
## Pre-Generation: READY

All 7 gates passed. Episode is ready for generation.

**Platform:** [heygen/synthesia]
**Duration:** ~X:XX
**Scenes:** X

Next: Open [platform] and paste the script.
Use `/vidcraft:heygen-engineer` or `/vidcraft:synthesia-engineer` to format.
```

If BLOCKED:
```
## Pre-Generation: BLOCKED

X gates failed. Fix these issues before generating:

1. [FAIL] Missing narration in Scene 3
2. [FAIL] Script not reviewed yet
```
