# AI Language Patterns — Red Flags for Video Narration

Shared knowledge base for AI-written language detection in video scripts and narration.
Used by: `voice-checker`, `script-reviewer`, `video-reviewer`.

## Tier 1: Hard Flags (almost always AI-generated)

Always flag, regardless of frequency:

- "In this comprehensive guide/tutorial/video"
- "Let's delve into / dive deep into"
- "Leverage" (instead of "use")
- "Utilize" (instead of "use")
- "It's important to note that"
- "In today's digital landscape"
- "Unlock the full potential"
- "Seamlessly integrate"
- "Robust and scalable"
- "Take your X to the next level"

## Tier 2: Soft Flags (AI-likely in narration context)

Flag if 2 or more appear per episode:

- "Furthermore" / "Moreover" (too formal for spoken narration)
- "Cutting-edge" / "State-of-the-art"
- "Streamline your workflow"
- "Empower you to"
- "Journey" (when not literal travel)
- "Landscape" (when not geography)
- "Navigate" (when not physical navigation)
- "Elevate your"
- Abstract noun chains: "the optimization of the implementation of the configuration"

## Tier 3: Pattern Flags

Flag if the pattern repeats across scenes:

- **Tricolon abuse:** "fast, reliable, and scalable" (always three adjectives)
- **Hedge stacking:** "might potentially help to possibly improve"
- **Empty intensifiers:** "truly", "really", "incredibly", "absolutely"
- **Generic scene openings:** every scene starts with "Now, let's..." or "Next, we'll..."
- **Over-explanation:** explaining obvious things the viewer can see

## Context Exceptions

Some flagged words are legitimate in specific contexts. Do not flag when:

- "navigate" refers to literal UI navigation (e.g., "navigate to Settings")
- "leverage" is used in a financial or business sense (leverage ratio, leveraged buyout)
- Tier 1 words match product or feature names (e.g., a product literally called "Comprehensive Mode")

## Quick Reference for Reviewers

When doing a quick check in reviewer skills, scan for these as shortlist indicators:

> "comprehensive", "leverage", "utilize", "delve", "seamlessly"

A hit on any of these warrants a full voice-checker run.
