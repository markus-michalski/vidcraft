# Video Type: How-To

## Overview

Practical, outcome-oriented videos that show viewers how to achieve a specific result. Unlike tutorials (which teach concepts step-by-step), how-tos focus on getting things done — less theory, more action. They assume some baseline familiarity and prioritize efficiency over explanation.

## Characteristics

| **Aspect** | **Value** |
|------------|-----------|
| **Duration** | 2-8 minutes |
| **Pacing** | Practical, hands-on, brisk |
| **Tone** | Competent, direct, no-nonsense |
| **WPM** | 130-140 (steady, action-oriented) |
| **Scene Changes** | Every 20-45 seconds |
| **Primary Visual** | Screencast + Avatar overlay |

## Structure Template

1. **Goal** (5-15s) — State the end result clearly: "By the end, you'll have..."
2. **Materials** (10-20s) — What's needed: tools, access, files, versions
3. **Steps** (60-300s) — Practical steps, grouped logically, focused on doing
4. **Result** (10-20s) — Show the finished outcome, confirm success
5. **CTA** (5-10s) — Related how-tos, documentation link, or next action

## Script Conventions

- State the goal in the first sentence — what will the viewer achieve?
- Skip background theory — link to explainer or tutorial videos for that
- Use imperative mood: "Open the file", "Add this line", "Save and restart"
- Group related steps into logical phases (e.g., "Setup", "Configuration", "Testing")
- Mention expected results after each major step: "You should now see..."
- Include common gotchas inline: "Make sure you're in the right directory"
- Max 18 words per sentence for action clarity

## Visual Direction

- **Primary:** Screencast with avatar overlay for narration guidance
- **Steps:** Full-screen screencast with cursor highlights, zoom on key areas
- **Transitions:** Hard cuts between steps, brief fade between phases
- **On-Screen Text:** Step numbers, commands/code, expected outputs, file paths
- **Annotations:** Arrows pointing to relevant UI elements, highlight boxes for inputs

## Pacing Rules

- Max 10 words of on-screen text at once
- No scene longer than 45 seconds
- Pause 1-2 seconds between steps (less than tutorials — assumes competent viewer)
- Show commands/code on screen for at least 4 seconds for readability
- If a step takes time (compilation, download), skip ahead with a note
- Total word count: 260-1100 words (scales with duration)

## Anti-Patterns

- Explaining the "why" at length — save that for tutorials or explainers
- Long introductions before getting to the first step
- Not showing the final result
- Assuming tools are installed without listing them in Materials
- Skipping over error-prone steps without mentioning potential issues
- Making the viewer wait through loading screens or progress bars

## Example Storyboard

```
Scene 1 (8s): Avatar — "Here's how to set up automatic backups for your OXID eShop database in under 5 minutes."
Scene 2 (12s): Avatar + Text overlay — "You'll need: SSH access, cron permissions, and mysqldump installed."
Scene 3 (35s): Screencast — Create the backup script, show the file contents, explain each line briefly
Scene 4 (25s): Screencast — Set up the cron job, show the crontab entry, highlight the schedule
Scene 5 (20s): Screencast — Run a manual test, show the backup file created with correct timestamp
Scene 6 (10s): Avatar — "Done. Your database now backs up every night at 2 AM. Check the link below for restore instructions."
```
