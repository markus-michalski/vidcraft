# VidCraft State Schema v1.0.0

## Overview

State is stored at `~/.vidcraft/cache/state.json` and rebuilt from markdown files on demand.

## Schema

```json
{
  "schema_version": "1.0.0",
  "plugin_version": "0.1.0-dev",
  "built_at": "2026-03-25T12:00:00+00:00",
  "config": { /* full config */ },
  "projects": {
    "<project-slug>": {
      "slug": "my-tutorial-series",
      "title": "My Tutorial Series",
      "video_type": "tutorial",
      "status": "Concept | Brief Complete | Research Done | Script Draft | Script Approved | Storyboard Done | Assets Ready | Generated | Reviewed | Published",
      "platform": "heygen | synthesia",
      "language": "de | en",
      "target_audience": "",
      "description": "",
      "created": "2026-03-25",
      "updated": "2026-03-25",
      "episode_count": 3,
      "episodes_data": {
        "<episode-slug>": {
          "slug": "01-getting-started",
          "title": "Getting Started",
          "number": 1,
          "status": "Not Started | Script Draft | Script Reviewed | Storyboard | Assets Collected | Ready for Generation | Generated | QA Passed | Final",
          "duration_target": "5:00",
          "platform": "heygen",
          "avatar": "",
          "description": "",
          "scene_count": 5,
          "scenes": {
            "<scene-stem>": {
              "file": "01-intro.md",
              "number": 1,
              "title": "Introduction",
              "status": "Outline | Script Written | Visual Defined | Assets Ready | Generated | Approved",
              "duration": "0:30",
              "visual_type": "avatar | screencast | slides | b-roll",
              "narration": "...",
              "on_screen_text": "...",
              "visual_direction": "...",
              "assets": "..."
            }
          }
        }
      }
    }
  },
  "ideas": [
    { "title": "Idea Title", "notes": "..." }
  ],
  "session": {
    "last_project": "my-tutorial-series",
    "last_episode": "01-getting-started",
    "last_phase": "Script Draft",
    "pending_actions": []
  }
}
```

## Status Progressions

### Project
```
Concept → Brief Complete → Research Done → Script Draft
→ Script Approved → Storyboard Done → Assets Ready
→ Generated → Reviewed → Published
```

### Episode
```
Not Started → Script Draft → Script Reviewed → Storyboard
→ Assets Collected → Ready for Generation → Generated
→ QA Passed → Final
```

### Scene
```
Outline → Script Written → Visual Defined → Assets Ready → Generated → Approved
```
