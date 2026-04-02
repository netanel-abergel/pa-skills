# Heleni — AI Personal Assistant Skills

Open-source skill library for [OpenClaw](https://openclaw.ai) AI Personal Assistant agents.
Built and battle-tested by [Heleni](https://netanel-abergel.github.io/pa-skills/), Netanel's production AI PA.

**Website:** https://netanel-abergel.github.io/pa-skills/

---

## Stay Updated — Auto-Sync for Any PA

Want your PA to automatically learn from Heleni's production lessons? Install the **[heleni-best-practices](skills/heleni-best-practices/)** skill. It runs daily, checks for new best practices, skill design rules, and library updates — then recommends or applies relevant changes to your agent.

```bash
# Quick install
git clone https://github.com/netanel-abergel/pa-skills.git
cp -r pa-skills/skills/heleni-best-practices /opt/ocana/openclaw/workspace/skills/
```

Once installed, your PA will:
- Fetch new lessons and skill updates daily (07:00 UTC)
- Compare against its last known state — only act on changes
- Log lessons to `.learnings/heleni-sync/` automatically
- Ask your approval before modifying SOUL.md or HOT.md
- Notify you only when something actionable is found

Trigger manually anytime: *"any updates from Heleni?"* or *"sync skills"*

---

## What Are Skills?

Skills are `SKILL.md`-based playbooks that give an AI agent step-by-step instructions for a specific domain. Each skill includes:

- **YAML frontmatter** — name, description, and trigger conditions
- **Playbook body** — steps, scripts, decision trees, and examples
- **Supporting files** — scripts, data templates, references (when needed)

```yaml
---
name: billing-monitor
description: "Monitor API billing errors and alert the owner. Use when: ..."
---
# Billing Monitor
## Step 1 — Detect billing errors
...
```

---

## Skills (20)

### Core

| Skill | Description |
|-------|-------------|
| [pa-onboarding](skills/pa-onboarding/) | Step-by-step setup wizard for new AI PAs on OpenClaw |
| [supervisor](skills/supervisor/) | Central status dashboard — tasks, issues, health, follow-ups |
| [owner-briefing](skills/owner-briefing/) | Daily briefing: meetings, emails, tasks, and action items |
| [skill-master](skills/skill-master/) | Meta-skill for routing — use when unsure which skill fits |
| [eval](skills/eval/) | Evaluate PA performance: tasks, skills, network health, memory quality |

### Communication

| Skill | Description |
|-------|-------------|
| [ai-pa](skills/ai-pa/) | Multi-agent PA coordination: contact peers, schedule across owners, broadcast messages |
| [meetings](skills/meetings/) | Schedule meetings via PA-to-PA coordination + summarize notes and transcripts |
| [whatsapp](skills/whatsapp/) | Per-conversation memory, unanswered message tracking, loop prevention, multi-PA coordination |

### Integrations

| Skill | Description |
|-------|-------------|
| [calendar-setup](skills/calendar-setup/) | Connect Google Calendar to an OpenClaw agent (setup, troubleshooting, permissions) |
| [monday-for-agents](skills/monday-for-agents/) | monday.com integration: boards, items, GraphQL API, MCP configuration |
| [youtube-watcher](skills/youtube-watcher/) | Fetch YouTube transcripts for summarization and Q&A |

### Self-Improvement

| Skill | Description |
|-------|-------------|
| [self-learning](skills/self-learning/) | Continuous improvement via logging, pattern detection, and behavioral updates |
| [self-monitor](skills/self-monitor/) | Health monitoring and infrastructure checks |
| [skill-analytics](skills/skill-analytics/) | Track skill usage across sessions — invocation logs, daily summaries, unused skill detection |
| [heleni-best-practices](skills/heleni-best-practices/) | Daily sync of production lessons from the pa-skills website |
| [skill-scout](skills/skill-scout/) | Automated daily discovery of new skills and PA automation ideas |
| [memory-tiering](skills/memory-tiering/) | Multi-tiered memory management (HOT/WARM/COLD) with automated pruning |

### Operations

| Skill | Description |
|-------|-------------|
| [maintenance](skills/maintenance/) | Workspace backup to GitHub + OpenClaw and skill updates |
| [billing-monitor](skills/billing-monitor/) | API billing error detection, alerting, and fallback model switching |

### Language

| Skill | Description |
|-------|-------------|
| [hebrew-nikud](skills/hebrew-nikud/) | Hebrew vowel-point reference for correct nikud in AI-generated text and TTS |

---

## Installation

### Install all skills

```bash
curl -fsSL https://netanel-abergel.github.io/pa-skills/install.sh | bash
```

### Install a single skill

```bash
# Clone and copy
git clone https://github.com/netanel-abergel/pa-skills.git
cp -r pa-skills/skills/billing-monitor /opt/ocana/openclaw/workspace/skills/
```

### Restart to activate

```bash
openclaw gateway restart
```

---

## Repository Structure

```
pa-skills/
├── skills/                  # Skill playbooks
│   ├── ai-pa/               #   Each skill has its own directory
│   │   └── SKILL.md         #   with a SKILL.md playbook
│   ├── billing-monitor/
│   ├── ...
│   └── README.md            # Categorized skill index
├── index.html               # GitHub Pages website
├── install.sh               # Batch installer script
├── heleni.jpg               # Heleni avatar
└── .github/workflows/       # Auto-deploy to GitHub Pages
```

---

## Contributing

1. Create a new directory: `skills/<skill-name>/`
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`)
3. Include a clear "Use when:" sentence in the description
4. Update `skills/README.md` and this file
5. Open a PR

### Skill design guidelines

- **One domain = one skill.** Users think in domains, not tools.
- **Keep the skill count between 28–32.** Above 40, routing breaks down.
- **Each skill needs one clear "Use when:" sentence** in the description.
- **Universal rules go in SOUL.md**, not in skills. Skills are triggered on demand.
- **Diagnostics = appendix.** Never a standalone skill.

---

## License

Open source. Use, fork, and adapt for your own AI PA agents.
