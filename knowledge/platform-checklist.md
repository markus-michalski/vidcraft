# Platform Checklist — HeyGen and Synthesia Constraints

Single source of truth for platform-specific limits and quirks. Skills
like `script-writer`, `heygen-engineer`, `synthesia-engineer`, and
`storyboard-creator` reference this file instead of duplicating the
rules.

For narration and on-screen-text rules that are platform-independent,
see [`script-writing-rules.md`](script-writing-rules.md).

## HeyGen

### Hard Constraints

| Constraint | Detail |
|------------|--------|
| One background per scene | One image, video, or color per HeyGen scene. Multiple backgrounds = split into multiple scenes. |
| No timed text overlays | Overlays are visible for the entire scene duration. Timed overlays must be done in post-production. |
| Max ~1500 characters per scene | Hard limit; split at natural pauses if exceeded. |
| Max scenes per video | Plan-dependent. Check current HeyGen plan. |
| One avatar per scene | No multi-avatar scenes. |

### Pause Support

HeyGen supports manual pauses inside narration:

| Marker | HeyGen behavior |
|--------|-----------------|
| `[pause 0.5s]` | 0.5 second pause |
| `[pause 1s]` | 1 second pause |
| Paragraph break | ~0.5 second pause (default) |

The same syntax is used in the source scripts (see
[`script-writing-rules.md`](script-writing-rules.md#pause-syntax)).

### Splitting Scenes for HeyGen

Split a content scene when:

- It exceeds 1500 characters
- It needs more than one background
- It needs to switch avatar

When splitting:

1. Cut at a natural pause point in the narration
2. Add a transition between the split scenes (cut or fade, defined
   in the storyboard)
3. Keep visual continuity (same brand frame, same lower-third)

### What Belongs in Post-Production

These cannot be done in HeyGen and must be planned for Shotcut /
Kdenlive / Premiere:

- Timed text overlays (overlays that appear at specific timestamps)
- Multi-track music with ducking
- Cross-scene transitions beyond cut/fade
- Picture-in-picture beyond HeyGen's avatar overlay
- Any animation that needs frame-precise timing

Mark these in scene scripts using the `[post-production ...]` syntax
(see [`script-writing-rules.md`](script-writing-rules.md#timed-overlays-post-production-marker)).

### HeyGen Scene Format

Each scene needs:

- **Script text** (narration)
- **Avatar** selection (see `/vidcraft:avatar-selector`)
- **Background** — exactly one per scene
- **Avatar position** — left, center, or right
- **Voice** selection
- **Speed** — 0.8x to 1.2x

## Synthesia

### Hard Constraints

| Constraint | Detail |
|------------|--------|
| Max ~1000 characters per slide | Slide-based; split at sentence boundary if exceeded. |
| Max slides per video | 50+ (plan-dependent). |
| Languages | 130+ supported. |
| Slide-based scene structure | 1 scene typically maps to 1 slide. |

### Slide Format

Each Synthesia slide needs:

- **Script** — narration text, max ~1000 characters
- **Avatar** selection (or "no avatar" for text-only slides)
- **Layout** — avatar left/right/center, with or without background media
- **Background** — solid color, image, video, or screen recording
- **Text overlays** — headlines, bullet points, key terms
- **Media** — images, screen recordings, animations

### Splitting Slides for Synthesia

Split a slide when it exceeds 1000 characters:

1. Cut at a natural sentence break
2. Use a transition slide for continuity
3. Keep related content on adjacent slides

### Layout Templates

| Scene Type | Recommended Layout |
|------------|--------------------|
| Intro / Outro | Avatar center, branded background |
| Explanation | Avatar left, key points right |
| Screencast | Screen recording full, avatar overlay corner |
| Comparison | Split screen, before/after |
| Summary | Text-only with bullet points |
| CTA | Avatar center, CTA text overlay |

## Cross-Platform Notes

These behaviors are the same in both platforms and worth knowing:

- Screen recordings should be captured separately (OBS, screen capture)
  and uploaded as background media — both platforms struggle with
  in-platform screen recording quality.
- Brand assets (logo, lower-third, color palette) are uploaded once and
  reused across scenes — define them in the project README.
- Voice cloning (paid feature on both platforms) requires a separate
  upload and approval flow — not covered by these skills.
