# PA Skills

OpenClaw skills for AI Personal Assistant agents.

## Skills

| Skill | Description |
|---|---|
| [ai-pa](./ai-pa/SKILL.md) | PA network directory, group coordination, scheduling templates |
| [billing-monitor](./billing-monitor/SKILL.md) | Detect and respond to API billing errors |
| [calendar-setup](./calendar-setup/SKILL.md) | Connect owner's Google Calendar with write access |
| [meeting-scheduler](./meeting-scheduler/SKILL.md) | Schedule meetings between owners via PA coordination |
| [monday-workspace](./monday-workspace/SKILL.md) | monday.com account setup, GraphQL API, and MCP server |
| [openclaw-email-orientation](./openclaw-email-orientation/SKILL.md) | Gmail and Google Calendar setup and troubleshooting |
| [owner-briefing](./owner-briefing/SKILL.md) | Daily morning briefing with meetings, emails, and tasks |
| [pa-onboarding](./pa-onboarding/SKILL.md) | Full step-by-step guide for setting up a new PA agent |
| [pa-status](./pa-status/SKILL.md) | Network health dashboard — monitor all PAs at once |
| [whatsapp-diagnostics](./whatsapp-diagnostics/SKILL.md) | Diagnose and fix WhatsApp connectivity issues |

## Usage

Each skill is a self-contained `SKILL.md` file. Install into your OpenClaw workspace:

```bash
# Copy a skill to your workspace
cp -r <skill-dir> ~/.openclaw/workspace/skills/

# Or install from this repo directly
openclaw skills install <skill-name>
```

## Contributing

Skills should be:
- Generic (no hardcoded personal data)
- Self-contained (all instructions in SKILL.md)
- Example data uses placeholders only
| [pa-eval](./pa-eval/SKILL.md) | Structured PA performance evaluation and scoring |
| [self-learning](./self-learning/SKILL.md) | Continuous self-improvement: capture, reflect, update behavior |
| [spawn-subagent](./spawn-subagent/SKILL.md) | Delegate long or blocking tasks to isolated subagents — keeps main session responsive |
| [skill-scout](./skill-scout/SKILL.md) | Weekly automated skill discovery — searches the web for new skill ideas and delivers a scored digest |
| [git-backup](./git-backup/SKILL.md) | Backup workspace to GitHub — token discovery, repo setup, auto-push |
| [group-memory](./group-memory/SKILL.md) | Separate memory context per WhatsApp group — prevents context bleed |
