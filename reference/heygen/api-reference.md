# HeyGen API Reference

## Overview

HeyGen provides a REST API for programmatic video creation. While vidcraft currently uses manual copy-paste, this reference prepares for future API integration.

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v2/video/generate` | POST | Create video from script + avatar |
| `/v1/video.list` | GET | List generated videos |
| `/v1/video_status.get` | GET | Check generation progress |
| `/v1/avatar.list` | GET | List available avatars |
| `/v1/voice.list` | GET | List available voices |

## Video Generation Payload

```json
{
  "video_inputs": [
    {
      "character": {
        "type": "avatar",
        "avatar_id": "...",
        "avatar_style": "normal"
      },
      "voice": {
        "type": "text",
        "input_text": "Narration text here",
        "voice_id": "..."
      },
      "background": {
        "type": "color",
        "value": "#FFFFFF"
      }
    }
  ],
  "dimension": {
    "width": 1920,
    "height": 1080
  }
}
```

## Avatar Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Stock** | Pre-made avatars | Quick start, prototyping |
| **Photo** | Generated from a single photo | Custom brand ambassador |
| **Studio** | Recorded in HeyGen studio | Highest quality, most natural |

## Voice Options

- **Text-to-Speech:** 300+ voices in 40+ languages
- **Voice Cloning:** Upload audio sample for custom voice
- **ElevenLabs:** Premium voice integration

## Limits (as of 2025)

| Limit | Free | Creator | Business |
|-------|------|---------|----------|
| Video length | 1 min | 20 min | 60 min |
| Videos/month | 3 | Unlimited | Unlimited |
| Resolution | 720p | 1080p | 4K |
| API access | No | No | Yes |

## Authentication

```
Authorization: Bearer {api_key}
```

API key from: HeyGen Dashboard → Settings → API

## Rate Limits

- 100 requests/minute for listing endpoints
- 10 concurrent video generations
- Webhook support for async generation status
