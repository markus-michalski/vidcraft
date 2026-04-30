# Synthesia API Reference

## Overview

Synthesia provides a REST API (STUDIO API) for programmatic video creation. While vidcraft currently uses manual workflow, this reference prepares for future integration.

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v2/videos` | POST | Create video from script |
| `/v2/videos/{id}` | GET | Get video status |
| `/v2/videos` | GET | List all videos |
| `/v2/avatars` | GET | List available avatars |
| `/v2/voices` | GET | List available voices |
| `/v2/templates` | GET | List video templates |

## Video Creation Payload

```json
{
  "title": "Video Title",
  "input": [
    {
      "scriptText": "Narration text for this slide",
      "avatar": "avatar_id",
      "avatarSettings": {
        "horizontalAlign": "center",
        "scale": 1.0,
        "style": "rectangular"
      },
      "background": {
        "videoUrl": null,
        "imageUrl": null,
        "color": "#FFFFFF"
      }
    }
  ],
  "aspectRatio": "16:9",
  "test": false
}
```

## Avatar Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Express** | AI-generated, quick setup | Standard content, 130+ languages |
| **Studio** | Recorded from real person | Premium brand content |
| **Custom** | Your own likeness | Personal brand, CEO messages |

## Voice Options

- **Built-in voices:** 130+ languages, multiple accents per language
- **Voice cloning:** Custom voice from audio sample
- **SSML support:** Fine-grained pronunciation control

## Limits (as of 2025)

| Limit | Starter | Creator | Enterprise |
|-------|---------|---------|------------|
| Videos/month | 10 | 30 | Unlimited |
| Minutes/month | 10 | 30 | Custom |
| Resolution | 1080p | 1080p | 1080p |
| API access | No | Yes | Yes |
| Custom avatars | No | No | Yes |

## Slide Structure

Each element in `input[]` is one slide:
- Max ~1000 characters per slide script
- Max 150 slides per video
- Slides can have different avatars and backgrounds
- Transitions are automatic (cut between slides)

## Gesture Tags (Express-1 avatars)

Inline gesture tags can be embedded directly in `scriptText` to trigger avatar gestures at specific points.

```
[gesture:nod]          — Avatar nods (agreement/confirmation)
[gesture:headyes]      — Head up/down twice
[gesture:headno]       — Head left/right twice (disagreement)
[gesture:eyebrowsup]   — Raised eyebrows (surprise/emphasis)
[gesture:increase]     — Arm/hand gesture for growth/expansion
```

**Usage:**
```
"We are seeing [gesture:increase] huge growth this quarter."
"Let me [gesture:nod] confirm that this is the correct approach."
```

**Constraints:**
- Gesture tags only work with **Express-1 avatars** — Express-2 generates gestures automatically from script context, so gesture tags are neither needed nor supported
- Use gestures sparingly — one per sentence at most
- Tags are stripped from the final audio; they only trigger animation

## SSML Support

Synthesia supports a subset of SSML for fine-grained speech control:

```xml
<break time="1s"/>     — Pause for 1 second
<break time="0.5s"/>   — Pause for 500ms
```

VidCraft formatters auto-convert `[pause Xs]` markers to `<break time="Xs"/>` — no manual conversion needed.

## Authentication

```
Authorization: {api_key}
```

API key from: Synthesia Dashboard → Settings → API Keys

## Webhook Support

```json
{
  "callbackUrl": "https://your-server.com/webhook",
  "callbackId": "custom-correlation-id"
}
```

Status updates: `processing` → `complete` or `error`
