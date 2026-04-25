# Status → Next Step Mapping

Single source of truth for status-based skill recommendations.
Consumed by `skills/resume/SKILL.md` (Project-level) and `skills/next-step/SKILL.md` (Episode-level + priority routing).

When adding or renaming a status, update **only this file** — both skills read from here.

## Project Status

Used by `resume` to recommend the next action for a whole project (coarse-grained view).

| Status | Next Skill | Notes |
|--------|------------|-------|
| Concept | `/vidcraft:project-conceptualizer` | Develop narrative and episode plan |
| Brief Complete | `/vidcraft:researcher` | Optional — only if research is needed for this project |
| Brief Complete | `/vidcraft:script-writer` | If research is done or not needed, jump straight to scripting |
| Research Done | `/vidcraft:script-writer` | — |
| Script Draft | `/vidcraft:script-reviewer` | — |
| Script Approved | `/vidcraft:storyboard-creator` | — |
| Storyboard Done | `/vidcraft:screenshot-planner` | Followed by `asset-collector`, then `shot-list-creator` |
| Assets Ready | `/vidcraft:pre-generation-check` | Gate — must PASS before generation |
| Generated | `/vidcraft:video-reviewer` | — |
| Reviewed | `/vidcraft:release-director` | — |
| Published | — | Series complete |

## Episode Status

Used by `next-step` to recommend the most impactful action across all episodes (fine-grained view, priority routing).

| Status | Next Skill | Notes |
|--------|------------|-------|
| Not Started | `/vidcraft:script-writer [episode]` | — |
| Script Draft | `/vidcraft:script-reviewer [episode]` | Highest priority — unblocks downstream work |
| Script Reviewed | `/vidcraft:storyboard-creator [episode]` | — |
| Storyboard | `/vidcraft:screenshot-planner [episode]` | Then `asset-collector`, `shot-list-creator` |
| Assets Collected | `/vidcraft:pre-generation-check [episode]` | Gate — blocks generation if FAIL |
| Ready for Generation | `/vidcraft:heygen-engineer [episode]` or `/vidcraft:synthesia-engineer [episode]` | Platform formatting, then manual generation in HeyGen/Synthesia |
| Generated | `/vidcraft:video-reviewer [episode]` | — |
| QA Passed | `/vidcraft:release-director [project]` | Episode-level done — release is project-level |
| Final | — | Episode complete |

## Priority Order (for `next-step`)

When multiple episodes are in different statuses, recommend in this order:

1. **No projects exist** → `/vidcraft:new-project`
2. **Project is Concept, no brief** → `/vidcraft:project-conceptualizer`
3. **Any episode in Script Draft** → review it first (unblocks pipeline)
4. **Any episode Not Started** → start the next script
5. **All scripts approved, no storyboard** → `/vidcraft:storyboard-creator`
6. **Storyboard done, assets missing** → `/vidcraft:asset-collector`
7. **Assets collected** → `/vidcraft:pre-generation-check`
8. **Pre-gen passed** → manual generation step (HeyGen/Synthesia)
9. **Generated, not reviewed** → `/vidcraft:video-reviewer`
10. **All episodes Final** → `/vidcraft:release-director`

## Rationale for Two Tables

The two skills operate at different granularities:

- **`resume`** answers *"where is this whole project?"* — uses **Project Status** (coarse).
- **`next-step`** answers *"what should I literally do in the next 30 minutes?"* — uses **Episode Status** + priority routing (fine).

A single flat table would either lose project-level summary semantics or over-promise episode-level precision. Keeping both, in one file, with shared terminology, is the compromise.
