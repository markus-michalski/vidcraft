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
- Max 50 slides per video
- Slides can have different avatars and backgrounds
- Transitions are automatic (cut between slides)

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
