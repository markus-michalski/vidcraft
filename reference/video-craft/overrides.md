# Override System

## Overview

Users can customize vidcraft behavior without modifying the plugin itself. Override files live in the user's content root at `{content_root}/overrides/`.

## Override Locations

```
{content_root}/overrides/
├── CLAUDE.md                # Custom workflow rules (loaded by Claude Code)
├── brand-guide.md           # Brand-specific terminology, tone, colors
├── script-style.md          # Custom narration style preferences
├── video-type-defaults.yaml # Override default durations, WPM, etc.
└── platform-presets.yaml    # Custom avatar IDs, voices, backgrounds
```

## How Overrides Work

1. Skills check for override files before applying defaults
2. Override files take precedence over plugin defaults
3. Overrides are NOT committed to the plugin repo — they're user-specific

## Override Files

### CLAUDE.md
Custom routing rules or workflow modifications.

```markdown
# Custom VidCraft Rules

- Always use German for narration
- Default avatar: avatar_id_xyz
- Skip brand-checker for internal videos
- Use informal "du" instead of "Sie"
```

### brand-guide.md
Company-specific brand definitions.

```markdown
# Brand Guide

## Terminology
- Use "Modul" not "Plugin" for OXID extensions
- Use "Shop" not "Store" for German content
- Product name always capitalized: "Gallery PRO"

## Tone
- Friendly but competent
- Use "du" (informal German)
- Avoid corporate speak

## Visual
- Primary: #2563EB
- Secondary: #10B981
- Font: Inter
- Logo: always top-left in intro/outro scenes
```

### script-style.md
Personal narration preferences.

```markdown
# Script Style

- Start tutorials with a direct statement, not a question
- Use short sentences (max 15 words, stricter than default 20)
- Always include "Tipp:" callouts for best practices
- German narration, English on-screen text for technical terms
```

### video-type-defaults.yaml
Override video type settings.

```yaml
tutorial:
  wpm: 125          # Slower than default 130
  max_scene_duration: 45  # Stricter than default 60
explainer:
  max_duration: 90   # Shorter than default 120
```

### platform-presets.yaml
Pre-configured platform settings.

```yaml
heygen:
  default_avatar: "josh_avatar_id"
  default_voice: "de-DE-ConradNeural"
  default_background: "#F5F5F5"
  speed: 0.95

synthesia:
  default_avatar: "anna_express_id"
  default_voice: "de-DE-KatjaNeural"
  default_background: "template_clean_white"
```
