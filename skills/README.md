# AI-PA Skill Library

Modular SKILL.md-based playbooks for OpenClaw AI Personal Assistant agents.
Each skill lives in its own directory and follows the standard `SKILL.md` format with YAML frontmatter.

## Quick Install

```bash
curl -fsSL https://netanel-abergel.github.io/pa-skills/install.sh | bash
```

Installs all skills, sets up directory structure, and creates starter files. ~2 minutes.

---

## The `.context` Pattern

Skills are fully generic — no hardcoded IDs, phones, or internal names.

Each PA adds a local `.context` file per skill with her own values:

```
skills/
  storage-router/
    SKILL.md      ← generic, synced here ✅
    .context      ← your IDs/phones/JIDs, stays private ✅
```

Add `skills/**/.context` to your `.gitignore`.  
Each SKILL.md has a "Load Local Context" section.

---

## Skills (32)

### Core

| Skill | Description |
|-------|-------------|
| [skill-master](skill-master/) | Meta-skill: routing table for picking the right skill |
| [supervisor](supervisor/) | Central status dashboard — tasks, issues, health, follow-ups |
| [owner-briefing](owner-briefing/) | Daily briefing: meetings, emails, tasks, action items |
| [pa-onboarding](pa-onboarding/) | Step-by-step setup wizard for new AI PAs on OpenClaw |
| [eval](eval/) | Full PA performance evaluation: tasks, skills, network, memory |
| [pa-eval](pa-eval/) | Structured PA scoring: weekly self-eval with owner feedback |

### Communication & Coordination

| Skill | Description |
|-------|-------------|
| [ai-pa](ai-pa/) | Multi-agent PA coordination: contact peers, schedule, broadcast |
| [heleni-whatsapp](heleni-whatsapp/) | WhatsApp memory, unanswered tracking, loop prevention, multi-PA |
| [meetings](meetings/) | Schedule meetings via PA-to-PA + summarize notes/transcripts |
| [meeting-notetaker](meeting-notetaker/) | Fetch and present meeting notes from monday.com Notetaker |
| [meeting-scheduler](meeting-scheduler/) | Schedule meetings by coordinating with peer PAs |

### Integrations

| Skill | Description |
|-------|-------------|
| [monday-for-agents](monday-for-agents/) | monday.com: boards, items, task tracking, project board templates |
| [calendar-setup](calendar-setup/) | Connect Google Calendar (setup, troubleshoot, write permissions) |
| [youtube-watcher](youtube-watcher/) | Fetch YouTube transcripts for summarization and Q&A |

### Routing & Storage

| Skill | Description |
|-------|-------------|
| [storage-router](storage-router/) | Decide where to save: monday.com vs GitHub vs local |

### Monitoring & Health

| Skill | Description |
|-------|-------------|
| [billing-monitor](billing-monitor/) | Detect API billing errors and alert owner + admin |
| [pa-status](pa-status/) | PA network health dashboard: billing, calendar, active status |

### Analytics & Costs

| Skill | Description |
|-------|-------------|
| [usage-costs](usage-costs/) | Token usage and cost reports: per session, per day, per week |
| [skill-analytics](skill-analytics/) | Track skill usage, daily reports, find unused skills |

### Self-Improvement

| Skill | Description |
|-------|-------------|
| [self-learning](self-learning/) | Log corrections and apply lessons. Maintains HOT.md. |
| [self-monitor](self-monitor/) | Infrastructure + security checks, disk/memory/service health |
| [skill-scout](skill-scout/) | Weekly search for new skill ideas from the PA community |
| [heleni-best-practices](heleni-best-practices/) | Daily sync of production lessons from pa-skills website |
| [pa-ownership](pa-ownership/) | Autonomous task tracking with retry loops and proactive updates |

### Memory & Context

| Skill | Description |
|-------|-------------|
| [memory-architecture](memory-architecture/) | Honcho-inspired memory: working / session / long-term tiers |
| [memory-tiering](memory-tiering/) | HOT/WARM/COLD memory compaction and archiving |
| [proactive-pa](proactive-pa/) | Proactive PA behavior: heartbeats, autonomous checks, initiative |

### Setup & Maintenance

| Skill | Description |
|-------|-------------|
| [git-backup](git-backup/) | Backup workspace to GitHub. Handles token, init, push. |
| [maintenance](maintenance/) | Workspace backup (every 6h) + OpenClaw updates (weekly) |
| [dynamic-temperature](dynamic-temperature/) | LLM temperature selection by task type |
| [spawn-subagent](spawn-subagent/) | Spawn isolated subagents for long/blocking tasks |
| [research-synthesizer](research-synthesizer/) | Multi-source research: parallel searches, dedup, cited answer |

---

## Skill Format

Each skill directory contains a `SKILL.md` with:

```yaml
---
name: skill-name
description: "What it does and when to use it."
---
```

Followed by the full playbook: steps, scripts, examples, and configuration.

Optionally, a `.context` file with agent-specific values (gitignored from this repo):

```bash
# skill-name — Local Context (not synced to pa-skills)
OWNER_PHONE=+1XXXXXXXXXX
BOARD_ID=12345678
```

---

## Skill Design Rules

1. **SKILL.md is always generic** — no IDs, phones, JIDs, or internal names
2. **Agent-specific data → `.context` file** (gitignored from pa-skills)
3. **One domain = one skill**
4. **Universal rules → SOUL.md** (skills are triggered on demand only)
5. **Each skill needs one clear "Use when:" sentence**
6. **Skill count sweet spot: 28–32** (above 40 = routing degrades)
7. **Privacy review before push** — scan for internal names, IDs, phone numbers

---

## Contributing

1. Create a directory under `skills/<skill-name>/`
2. Add a `SKILL.md` with proper frontmatter and playbook
3. No hardcoded personal data — use `.context` pattern
4. Submit a PR

See the [website](https://netanel-abergel.github.io/pa-skills/) for the full learnings library.
