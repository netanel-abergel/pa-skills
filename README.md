# AI-PA Ecosystem

Open-source skill library for [OpenClaw](https://openclaw.ai) AI Personal Assistant agents.

## Structure

```
pa-skills/
  skills/           <- SKILL.md-based playbooks
  index.html        <- GitHub Pages site
  install.sh        <- Skill installer
```

## Skills

Skills are modular playbooks that guide agent behavior for specific tasks. Each skill has a `SKILL.md` with YAML frontmatter defining its name, description, and trigger conditions.

| Skill | Description |
|-------|-------------|
| [ai-pa](skills/ai-pa/) | Multi-agent PA coordination and peer messaging |
| [billing-monitor](skills/billing-monitor/) | API billing error detection, alerting, and fallback switching |
| [calendar-setup](skills/calendar-setup/) | Connect Google Calendar to an OpenClaw agent |
| [eval](skills/eval/) | Evaluate PA tasks, skills, network health, and memory quality |
| [hebrew-nikud](skills/hebrew-nikud/) | Hebrew vowel-point reference for nikud and TTS |
| [heleni-best-practices](skills/heleni-best-practices/) | Daily sync of best practices from the pa-skills website |
| [maintenance](skills/maintenance/) | Workspace backup to GitHub + OpenClaw/skill updates |
| [meetings](skills/meetings/) | Schedule meetings via PA coordination + summarize notes |
| [memory-tiering](skills/memory-tiering/) | Multi-tiered memory management (HOT/WARM/COLD) |
| [monday-for-agents](skills/monday-for-agents/) | monday.com boards, items, GraphQL API, and MCP config |
| [owner-briefing](skills/owner-briefing/) | Daily briefing: meetings, emails, tasks, action items |
| [pa-onboarding](skills/pa-onboarding/) | Step-by-step setup wizard for new PAs |
| [self-learning](skills/self-learning/) | Continuous improvement via logging and pattern detection |
| [self-monitor](skills/self-monitor/) | Health monitoring and infrastructure checks |
| [skill-master](skills/skill-master/) | Meta-skill for skill selection and routing |
| [skill-scout](skills/skill-scout/) | Automated daily discovery of new skills and ideas |
| [supervisor](skills/supervisor/) | Central status dashboard for the PA agent |
| [whatsapp](skills/whatsapp/) | Per-conversation memory, message tracking, loop prevention |
| [youtube-watcher](skills/youtube-watcher/) | Fetch YouTube transcripts for summarization and Q&A |

See [skills/README.md](skills/README.md) for categorized details.

## Install a Skill

```bash
# Using the installer
./install.sh billing-monitor

# Or manually
cp -r skills/billing-monitor /opt/ocana/openclaw/workspace/skills/
```

## Contributing

1. Create `skills/<skill-name>/SKILL.md` with proper frontmatter
2. Update both `README.md` and `skills/README.md`
