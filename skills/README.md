# AI-PA Skill Library

Modular SKILL.md-based playbooks for OpenClaw AI Personal Assistant agents. Each skill lives in its own directory and follows the standard `SKILL.md` format with YAML frontmatter.

## Skills

### Core

| Skill | Description |
|-------|-------------|
| [pa-onboarding](pa-onboarding/) | Step-by-step setup wizard for new AI PAs on OpenClaw |
| [supervisor](supervisor/) | Central status dashboard — tasks, issues, health, follow-ups |
| [owner-briefing](owner-briefing/) | Daily briefing: meetings, emails, tasks, and action items |
| [skill-master](skill-master/) | Meta-skill for skill selection and routing — use when unsure which skill fits |
| [eval](eval/) | Evaluate PA tasks, skills, network health, billing, and memory quality |

### Communication

| Skill | Description |
|-------|-------------|
| [ai-pa](ai-pa/) | Multi-agent PA coordination: contact peers, schedule across owners, broadcast messages |
| [meetings](meetings/) | Schedule meetings via PA-to-PA coordination + summarize notes and transcripts |
| [whatsapp](whatsapp/) | Per-conversation memory, unanswered message tracking, loop prevention, multi-PA coordination |

### Integrations

| Skill | Description |
|-------|-------------|
| [calendar-setup](calendar-setup/) | Connect Google Calendar to an OpenClaw agent (setup, troubleshooting, permissions) |
| [monday-for-agents](monday-for-agents/) | monday.com integration: boards, items, GraphQL API, MCP configuration |
| [youtube-watcher](youtube-watcher/) | Fetch YouTube transcripts for summarization and Q&A |

### Self-Improvement

| Skill | Description |
|-------|-------------|
| [self-learning](self-learning/) | Continuous improvement via logging, pattern detection, and behavioral updates |
| [self-monitor](self-monitor/) | Health monitoring and infrastructure checks |
| [skill-analytics](skill-analytics/) | Track skill usage across sessions — logs invocations, generates daily summaries, spots unused skills |
| [heleni-best-practices](heleni-best-practices/) | Daily sync of best practices from the pa-skills website |
| [skill-scout](skill-scout/) | Automated daily discovery of new skills and PA automation ideas |
| [memory-tiering](memory-tiering/) | Multi-tiered memory management (HOT/WARM/COLD) with automated pruning |

### Operations

| Skill | Description |
|-------|-------------|
| [maintenance](maintenance/) | Workspace backup to GitHub + OpenClaw/skill updates |
| [billing-monitor](billing-monitor/) | API billing error detection, alerting, and fallback model switching |

### Language

| Skill | Description |
|-------|-------------|
| [hebrew-nikud](hebrew-nikud/) | Hebrew vowel-point reference for correct nikud in AI-generated text and TTS |

## Skill Format

Each skill directory contains a `SKILL.md` with:

```yaml
---
name: skill-name
description: "What it does and when to use it."
---
```

Followed by the full playbook: steps, scripts, examples, and configuration.

## Installation

Copy a skill directory into your OpenClaw workspace:

```bash
cp -r skills/billing-monitor /opt/ocana/openclaw/workspace/skills/
```

Or reference it directly in your agent's system prompt.

## Contributing

1. Create a directory under `skills/<skill-name>/`
2. Add a `SKILL.md` with proper frontmatter
3. Update this README with your addition
