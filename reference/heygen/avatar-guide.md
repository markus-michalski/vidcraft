# HeyGen Avatar Selection Guide

## Avatar Categories

### By Appearance

| Category | Example Use Cases | Notes |
|----------|-------------------|-------|
| **Professional** | B2B demos, corporate training | Suit/blazer, neutral background |
| **Casual** | Developer tutorials, SaaS onboarding | Polo, hoodie, modern office |
| **Friendly** | Consumer products, FAQ videos | Bright colors, warm smile |
| **Authoritative** | Compliance training, announcements | Formal, confident posture |

### By Demographics

Choose avatars that match or resonate with your target audience:
- **Age range:** Match to audience median (younger for tech, older for enterprise)
- **Gender:** Consider audience composition; when unsure, test both
- **Ethnicity:** Diverse representation, match to primary market

## Position & Framing

| Position | When to Use |
|----------|-------------|
| **Center** | Intro/outro, CTA, important announcements |
| **Left third** | When showing content on the right (split layout) |
| **Right third** | When showing content on the left |
| **Small overlay** | During screencast — bottom-right corner |
| **Hidden** | Pure screencast or text-only slides |

## Avatar IV — Motion Prompts (May 2025)

HeyGen Avatar IV uses a Diffusion-inspired audio-to-expression engine. Custom gesture control is done via **Motion Prompts** — natural language sentences set per scene.

**Syntax:** `[Body part] + [Action] + [Emotion/Intensity]`

```
"Right arm raises to wave enthusiastically."
"Nods gently to emphasize agreement."
"Points forward with confidence."
"Looks surprised and raises eyebrows."
"Avatar smiles softly while raising a hand."
```

**Rules:**
- One short sentence — no compound actions per prompt
- Available verbs: point, nod, turn, wave, smile, look surprised, smile gently
- Set in HeyGen AI Studio → Avatar → Motion Prompt (per scene)
- Only available for Avatar IV avatars — verify avatar generation before committing

**Legacy gesture styles** (pre-Avatar IV) are still available as broad categories:
- **Neutral** — Default stance, minimal movement
- **Pointing** — Direct attention to on-screen elements
- **Open hands** — Welcoming, explaining concepts
- **Nodding** — Affirming tone

## Background Recommendations

| Video Type | Background |
|-----------|------------|
| Tutorial | Clean office or gradient |
| Product Demo | Branded color or product screenshot (blurred) |
| Training | Neutral solid color (#F5F5F5 light, #2D2D2D dark) |
| Onboarding | Company-branded, warm tones |

## Voice Pairing

- Always preview avatar + voice combination
- Match voice gender to avatar appearance
- For German: verify umlauts (ä, ö, ü) pronunciation
- Speed: 1.0x default, adjust after first test generation
