# Video Type: Installation Guide

## Overview

Focused videos that walk viewers through installing, configuring, and verifying software, plugins, or services. More structured and sequential than general tutorials, with emphasis on prerequisites, exact commands, and troubleshooting common errors.

## Characteristics

| **Aspect** | **Value** |
|------------|-----------|
| **Duration** | 2-8 minutes |
| **Pacing** | Clear, sequential, methodical |
| **Tone** | Precise, confident, supportive |
| **WPM** | 130-140 |
| **Scene Changes** | Every 20-60 seconds |
| **Primary Visual** | Screencast (terminal/browser) + Avatar |

## Structure Template

1. **Introduction** (5-10s) — What we're installing and why
2. **Prerequisites** (15-30s) — System requirements, accounts, tools needed
3. **Download/Obtain** (20-40s) — Where to get the software
4. **Installation Steps** (60-180s) — Step-by-step installation process
5. **Configuration** (30-60s) — Initial setup and configuration
6. **Verification** (15-30s) — Confirm installation succeeded
7. **Troubleshooting** (20-40s) — Common issues and fixes
8. **Wrap-up / CTA** (5-10s)

## Script Conventions

- Always start with exact version numbers: "We're installing version 7.2"
- Show every command in full, letter by letter if relevant
- Read out file paths explicitly: "Navigate to slash var slash www"
- Always show the expected output after each command
- Include exact error messages for troubleshooting section
- Use conditional language for platform differences: "If you're on Ubuntu..."

## Visual Direction

- **Primary:** Screencast (terminal or browser, full-screen)
- **Avatar:** Appear at start/end, avatar overlay during complex explanations
- **Commands:** Show as on-screen text overlays (large, monospace font)
- **Transitions:** Hard cuts between steps, no fancy transitions
- **Highlights:** Red box around important UI elements, terminal line highlights
- **Screenshots:** Terminal output BEFORE and AFTER each command

## Pacing Rules

- One command per scene maximum
- Pause 3 seconds after showing terminal output
- On-screen text for every command (even if narrated)
- Max 60 seconds per installation step
- Total word count: 300-1000 words

## Anti-Patterns

- Skipping prerequisite checks
- Not showing expected output/confirmation
- Glossing over configuration options
- Missing troubleshooting section
- Not mentioning version numbers
- Assuming specific OS without stating it

## Example Storyboard

```
Scene 1 (8s): Avatar — "Let's install the OXID eShop Gallery Module in under 5 minutes."
Scene 2 (15s): Slides — Prerequisites list: PHP 8.2+, Composer, OXID 7.x
Scene 3 (25s): Screencast — Terminal: composer require command + output
Scene 4 (20s): Screencast — Terminal: vendor/bin/oe-console module:activate
Scene 5 (30s): Screencast — Browser: Admin → Extensions → verify module listed
Scene 6 (20s): Screencast — Browser: Frontend → verify gallery appears
Scene 7 (15s): Avatar — "If you see error XY, check that PHP extensions are loaded."
Scene 8 (7s): Avatar — "Done! Check the docs for configuration options."
```
