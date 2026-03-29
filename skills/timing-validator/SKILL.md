---
name: timing-validator
description: "Quick validation of episode timing against video type conventions. Checks total duration, scene durations, and pacing rhythm."
argument-hint: "<project-slug> <episode-slug>"
model: claude-haiku-4-5-20251001
user-invocable: true
allowed-tools:
  - Read
  - mcp__vidcraft-mcp__get_project_full
  - mcp__vidcraft-mcp__get_episode
  - mcp__vidcraft-mcp__list_scenes
  - mcp__vidcraft-mcp__analyze_timing
---

# Timing Validator

Fast timing check against video type conventions. Uses Haiku for speed.

## Checks

1. **Total duration** vs. type range (e.g., tutorial: 3-15 min)
2. **Scene count** — enough visual variety?
3. **Longest scene** — any scene over 60s?
4. **Shortest scene** — any scene under 5s? (too abrupt)
5. **Hook duration** — first scene under 10s?
6. **WPM** — within type's target range?

## Output

```
# Timing: [Episode]

| Check | Value | Target | Result |
|-------|-------|--------|--------|
| Duration | 4:30 | 3-15 min | PASS |
| Scenes | 8 | 5+ | PASS |
| Longest | 55s (Scene 4) | <60s | PASS |
| Shortest | 3s (Scene 7) | >5s | WARN |
| Hook | 8s | <10s | PASS |
| WPM | 138 | 120-140 | PASS |

**Verdict:** PASS (1 warning)
```
