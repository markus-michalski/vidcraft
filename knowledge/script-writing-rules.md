# Script Writing Rules — Single Source of Truth

These rules apply to all narration written for AI-generated videos
(HeyGen, Synthesia, or any other avatar platform). Skills like
`script-writer`, `script-reviewer`, `storyboard-creator`, and
`heygen-engineer` reference this file instead of duplicating the rules.

For platform-specific constraints (character limits, background rules,
overlay timing) see [`platform-checklist.md`](platform-checklist.md).

## Narration Rules

| Rule | Why |
|------|-----|
| Max 20 words per sentence | Avatars sound unnatural in long sentences |
| Use active voice ("Click the button") | Direct, viewer-focused |
| Address the viewer with "you" | Builds connection |
| Avoid filler words: "basically", "actually", "just", "really" | Cuts run-time without losing meaning |
| Write for spoken delivery, not for reading | Punctuation = breath, not grammar |

### Pause Syntax

Both HeyGen and the storyboard format use the same pause markers in
narration text. Keep them in the script source so all downstream tools
(`heygen-engineer`, `storyboard-creator`) can interpret them.

| Marker | Meaning |
|--------|---------|
| `[pause 0.5s]` | Short breath between paragraphs |
| `[pause 1s]` | Standard pause between topics |
| Paragraph break (blank line) | Implicit ~0.5s pause |

`[pause]` without a duration is allowed for legacy scripts and is
interpreted as 2 seconds. Prefer the explicit form in new scripts.

## Expressive Avatar Emotion Cues (Synthesia)

Synthesia Expressive Avatars (Express-1 and Express-2) analyse script
sentiment automatically. Punctuation and word choice directly drive
avatar expression — use this intentionally.

| Trigger | Avatar Effect |
|---------|--------------|
| `!` | Enthusiasm, positive energy, eyebrow lift |
| `?` | Inquisitive expression, slight head tilt |
| `...` | Thoughtful pause, reflective look |
| `:)` | Subtle smile, warm expression |
| `:(` | Concern, serious expression |
| Strong positive words: "Fantastic!", "Great job!" | Micro-smile |
| Negative words: "Unfortunately", "Problem" | Subtle frown, concern |

**Express-2:** same triggers, but with stronger full-body reinforcement
(see [`platform-checklist.md`](platform-checklist.md) for Express-2 details).

### Usage guidelines

- Use `!` at key reveals, success moments, and call-to-actions
- Use `?` when introducing a problem or posing a question to the viewer
- Use `...` for dramatic pauses before reveals
- Avoid flatline scripts: >60 seconds of narration with zero `!` or `?`
  will make the avatar appear expressionless
- Emoticons (`:)` `:(`): note these are processed by Synthesia — use
  sparingly and only when tone warrants it

### HeyGen note

HeyGen avatars do **not** use punctuation-based sentiment analysis.
These cues are Synthesia-specific.

## On-Screen Text Rules

| Rule | Why |
|------|-----|
| Max 7 words per overlay | Readable in 2-3 seconds |
| Use for: key terms, commands, URLs, step numbers | High signal density |
| Never duplicate the narration verbatim | Wastes the visual channel |
| Use for emphasis, not redundancy | If both channels say the same thing, drop one |

### Timed Overlays (Post-Production Marker)

HeyGen does not support overlays that appear/disappear at specific
timestamps within a scene — overlays are visible for the entire scene
duration (see [`platform-checklist.md`](platform-checklist.md#heygen)).

If you need timed overlays, mark them in the scene script for
post-production tools (Shotcut, Kdenlive):

```
[post-production overlay: "Save the file" at 00:12-00:15]
```

The `heygen-engineer` strips these markers before sending the script
to HeyGen and surfaces them in the post-production task list.

## Visual Direction Basics

These apply to every scene file, regardless of visual type. The
`storyboard-creator` enriches them with platform-specific details.

- Be specific: "Show terminal with cursor on line 5", not "Show terminal"
- Name transitions: "Fade from avatar to screencast"
- Mention avatar gestures when intentional: "Avatar points right to
  highlight the sidebar"
- Specify highlights: "Red box around the Submit button", not
  "highlight the button"

## Variable Placeholders (HeyGen Personalized Videos)

Use `{{snake_case}}` placeholders for dynamic content in personalized video campaigns.

```
{{first_name}}, welcome to {{company_name}}!
Your plan: {{plan_name}} — renews on {{renewal_date}}.
```

**Rules:**
- Always `{{snake_case}}` — no spaces, no camelCase, no hyphens
- URLs in `{{variables}}` go **on-screen only** — never narrate a URL
- All placeholders must be declared in HeyGen Template API before generating
- `heygen_format_script` auto-detects and lists all `{{variables}}` found

See [`platform-checklist.md`](platform-checklist.md#variable-injection) for
variable types (text, image, video, audio, avatar) and naming conventions.

## SSML Prosody Markup (HeyGen, community-verified)

Use SSML prosody tags sparingly and only when rewriting the sentence
does not solve the problem. These tags require **Custom Voice** and are
community-verified — not officially documented by HeyGen.

| Situation | Preferred fix | SSML fallback |
|-----------|--------------|---------------|
| Complex command sequence | Break into shorter sentences | `<prosody rate="slow">...</prosody>` |
| Key term needs emphasis | Restructure sentence | `<emphasis level="strong">...</emphasis>` |
| Section transition pause | Use paragraph break | `<p>...</p>` |
| ALL-CAPS for emphasis | Never use ALL-CAPS in scripts | `<emphasis level="strong">...</emphasis>` |

**Decision rule:** If you can fix it by rewriting the sentence → rewrite. Resort
to SSML only when the structural fix would break the natural spoken flow.

Always carry the disclaimer in output:

```
⚠️ Community-verified SSML — not in official HeyGen docs.
   Requires Custom Voice. Test with a short scene first.
```

See [`platform-checklist.md`](platform-checklist.md#ssml-prosody-tags-community-verified)
for the full supported tag list.

## Pronunciation Guide (TTS)

TTS engines on both HeyGen and Synthesia struggle with numbers and acronyms.
Use `check_pronunciation()` to scan before finalizing. Rules:

| Pattern | Problem | Fix |
|---------|---------|-----|
| Year: `2025` | "two thousand twenty-five" | "twenty twenty-five" |
| Year: `1990` | "one thousand nine hundred ninety" | "nineteen ninety" |
| Acronym: `API` | "appi" | "A P I" (spell out) or "Application Programming Interface (API)" on first use |
| Acronym: `HTTPS` | "huh-tips" | "H T T P S" |
| `e.g.` | "ee gee" | "for example" |
| `i.e.` | "eye ee" | "that is" |
| `etc.` | "et-see" | "and so on" |
| `v2.1` | context-dependent | usually fine — test first |
| `100,000` | "one hundred thousand" | usually fine |

**Rule:** `check_pronunciation()` flags issues, user approves each fix.
Never auto-replace — context determines the right spoken form.

Platforms also offer built-in pronunciation tools:
- **HeyGen:** Brand Glossary (workspace-wide custom pronunciations)
- **Synthesia Enterprise:** Pronunciation Dictionary

## Anti-Patterns

- AI-sounding language ("In this comprehensive guide", "Let's delve
  into") — see [`ai-language-patterns.md`](ai-language-patterns.md)
- Wall of text narration without visual changes
- Missing CTA at the end of the episode
- Inconsistent tone across scenes (set tone in project README, hold to it)
