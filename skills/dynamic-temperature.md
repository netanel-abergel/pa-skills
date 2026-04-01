# Dynamic Temperature Guide

Recommended temperature settings by task type.
Apply these in skill prompts or model_config sections.

| Task Type | Temperature | Use When |
|---|---|---|
| Irreversible actions | 0.0 | Deleting calendar events, sending official emails, destructive ops |
| Scheduling / CLI | 0.1–0.2 | Meeting coordination, commands, dates, facts |
| Analysis / Planning | 0.3–0.4 | Structured thinking, summaries, status reports |
| General communication | 0.5–0.6 | Daily chat, WhatsApp replies, updates |
| Briefings / Emails | 0.6–0.7 | Morning briefing, drafting messages with warmth |
| Creative writing | 0.8–0.9 | Jokes, stories, creative content |

## Rule of Thumb
- More precision needed → lower temperature
- More warmth/creativity needed → higher temperature
- When in doubt: 0.5

## Per-Skill Recommendations
- `owner-briefing`: 0.6 (warm but structured)
- `meeting-scheduler`: 0.2 (precise)
- `ai-meeting-notes`: 0.3 (factual summaries)
- `supervisor`: 0.2 (status facts)
- `billing-monitor`: 0.1 (alerts must be accurate)
- `git-backup`: 0.0 (no creativity needed)
