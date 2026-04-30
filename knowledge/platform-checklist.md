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
| Max 5000 characters per scene | Hard API limit. AI Studio (copy/paste) auto-splits at ~1000 chars/segment — no manual splitting needed for length. Only split manually for background or avatar changes. |
| Max scenes per video | Plan-dependent. Check current HeyGen plan. |
| One avatar per scene | No multi-avatar scenes. |

### Pause Support

> **Important:** Pause markers and SSML tags only work with **Custom Voices** (voice clones,
> ElevenLabs, OpenAI Voices). The public HeyGen Voice Library silently ignores all pause syntax.

| Marker | HeyGen behavior | Requirement |
|--------|-----------------|-------------|
| `[pause 0.5s]` | 0.5 second pause | Custom Voice only |
| `[pause 1s]` | 1 second pause | Custom Voice only |
| Paragraph break | ~0.5 second pause (default) | All voices |

**Fallback for public voices:** Use punctuation-based pacing instead:
- `,` → short pause (~300ms)
- `.` → longer pause (~600ms) with falling intonation
- `-` → syllable break for pronunciation clarity

The same syntax is used in the source scripts (see
[`script-writing-rules.md`](script-writing-rules.md#pause-syntax)).

### Splitting Scenes for HeyGen

Split a content scene when:

- It needs more than one background
- It needs to switch avatar

> The 5000-char API limit is rarely hit in practice. AI Studio auto-splits long segments at ~1000
> chars — no manual intervention needed for length alone.

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

### SSML Prosody Tags (Community-Verified)

> ⚠️ **Community-verified only — NOT in official HeyGen documentation.**
> Works with: Custom Voice Clones, ElevenLabs, OpenAI Voices.
> **Test with a short scene before applying to full video.**

The following SSML subset has been verified by the community to work in HeyGen (2025):

```xml
<prosody rate="x-slow">...</prosody>   <!-- Speed: x-slow, slow, medium, fast, x-fast -->
<prosody pitch="high">...</prosody>    <!-- Pitch: x-low, low, medium, high, x-high -->
<prosody volume="loud">...</prosody>   <!-- Volume: silent, x-soft, soft, medium, loud, x-loud -->
<emphasis level="strong">...</emphasis>  <!-- Emphasis: strong, moderate, reduced -->
<p>...</p>                             <!-- Paragraph pause (~400-800ms) -->
<s>...</s>                             <!-- Sentence pause (~200-400ms) -->
```

**Not supported:** `<phoneme>`, `<audio>`, `<lang>` (partial).

**Use cases:**
```xml
<!-- Slow down for technical or complex content -->
<prosody rate="slow">Run the command: docker compose up -d.</prosody>

<!-- Emphasize a key point (preferred over ALL-CAPS) -->
This is <emphasis level="strong">critical</emphasis> — do not skip this step.

<!-- Section break -->
<p>That covers installation.</p><p>Now let's look at configuration.</p>
```

**Rules:**
- Do NOT auto-convert — user must explicitly opt in
- Always include the community disclaimer in output when these tags are used
- Only works with **Custom Voices** — the pre-generation check will warn otherwise
- Use `<emphasis>` instead of ALL-CAPS for emphasis (more portable, cleaner script)

### Voice Director

Control vocal tone per scene via **emotion presets** or natural language prompts (HeyGen AI Studio → Voice → Voice Director).

| Preset | Best For |
|--------|----------|
| `Casual` | Tutorials, developer content |
| `Calm` | Support, step-by-step explanations |
| `Excited` | Product launches, CTAs |
| `Serious` | Compliance, authoritative content |
| `Cool` | Thought leadership, brand |

Free-form alternative: `"Speak in a warm, encouraging tone."` — set as a natural language prompt.

Recommendation: always set Voice Director explicitly; the default neutral tone rarely matches the content mood.

### Avatar IV — Motion Prompts

HeyGen Avatar IV (May 2025) supports custom gesture control via natural language **Motion Prompts**.

**Syntax:** `[Body part] + [Action] + [Emotion/Intensity]`

```
"Right arm raises to wave enthusiastically."
"Nods gently to emphasize agreement."
"Points forward with confidence."
"Looks surprised and raises eyebrows."
"Avatar smiles softly while raising a hand."
```

**Rules:**
- One short sentence per prompt — no compound actions
- Available verbs: point, nod, turn, wave, smile, look surprised, smile gently
- Set in HeyGen AI Studio → Avatar → Motion Prompt field (per scene)
- Only available for Avatar IV avatars — check avatar generation when selecting

### HeyGen Scene Format

Each scene needs:

- **Script text** (narration)
- **Avatar** selection (see `/vidcraft:avatar-selector`)
- **Background** — exactly one per scene
- **Avatar position** — left, center, or right
- **Voice** selection + **Voice Director** preset or prompt
- **Speed** — 0.8x to 1.2x
- **Motion Prompt** (Avatar IV only, optional)

## Synthesia

### Hard Constraints

| Constraint | Detail |
|------------|--------|
| Max ~1000 characters per slide | Slide-based; split at sentence boundary if exceeded. |
| Max scenes per video | 150 (PowerPoint import: also 150 slides). |
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

### Gesture Tags (Express-1 avatars only)

Embed inline gesture tags in script text to trigger avatar animations:

```
[gesture:nod]        — Nod (agreement)
[gesture:headyes]    — Head up/down twice
[gesture:headno]     — Head left/right (disagreement)
[gesture:eyebrowsup] — Raised eyebrows (surprise/emphasis)
[gesture:increase]   — Arm gesture for growth/expansion
```

Example: `"We are seeing [gesture:increase] huge growth this quarter."`

**Important:** Gesture tags are only for **Express-1** avatars. Express-2 generates gestures automatically — do not add gesture tags to Express-2 scripts.

### Express-2 Avatars (September 2025)

Synthesia released Express-2 — a Diffusion Transformer-based model that changes how gestures and expressions work.

| Feature | Express-1 | Express-2 |
|---------|-----------|-----------|
| Gestures | Manual `[gesture:tag]` syntax | Automatic from script context |
| Expressions | Sentiment-driven | Full-body co-speech gestures |
| Body language | Upper-body only | Full-body movement |
| Script requirements | Explicit gesture tags | Strong verbs + concrete actions |

**Writing for Express-2:**
- No gesture tags needed — they will be ignored
- Use active, concrete language: strong verbs and specific actions trigger gestures naturally
- Passive/abstract scripts produce no gestures — avatar appears stiff
- Example: "Click the button" (good) vs. "The button should be clicked" (stiff)

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
