# AI-PA Ecosystem

A collection of OpenClaw skills and plugins for AI Personal Assistants.

## Structure

```
pa-skills-repo/
  skills/     ← AgentSkill playbooks (SKILL.md-based)
  plugins/    ← OpenClaw JS/TS plugins
```

---

## 🧠 Skills

Skills are SKILL.md-based playbooks that guide agent behavior for specific tasks.

**Available skills:**

| Skill | Description |
|-------|-------------|
| [ai-pa](skills/ai-pa/) | Multi-agent PA coordination |
| [billing-monitor](skills/billing-monitor/) | Monitor API billing and alert on failures |
| [calendar-setup](skills/calendar-setup/) | Connect Google Calendar to your agent |
| [eval](skills/eval/) | Evaluate PA tasks, skills, and health |
| [git-backup](skills/git-backup/) | Backup workspace to GitHub |
| [meeting-scheduler](skills/meeting-scheduler/) | Schedule meetings via PA-to-PA coordination |
| [monday-for-agents](skills/monday-for-agents/) | monday.com integration for agents |
| [openclaw-email-orientation](skills/openclaw-email-orientation/) | Email/calendar setup orientation |
| [owner-briefing](skills/owner-briefing/) | Daily briefing for the owner |
| [pa-eval](skills/pa-eval/) | PA performance scoring |
| [pa-onboarding](skills/pa-onboarding/) | New PA setup wizard |
| [pa-status](skills/pa-status/) | PA network health dashboard |
| [self-learning](skills/self-learning/) | Continuous self-improvement |
| [skill-master](skills/skill-master/) | Skill selection and routing |
| [skill-scout](skills/skill-scout/) | Daily skill discovery |
| [spawn-subagent](skills/spawn-subagent/) | Spawn isolated subagents |
| [supervisor](skills/supervisor/) | Central PA status dashboard |
| [whatsapp-diagnostics](skills/whatsapp-diagnostics/) | WhatsApp connectivity troubleshooting |
| [whatsapp-memory](skills/whatsapp-memory/) | Per-conversation memory contexts |

### Install a skill

Copy the skill directory into your OpenClaw workspace:

```bash
cp -r skills/billing-monitor /opt/ocana/openclaw/workspace/skills/
```

Or reference it directly in your agent's system prompt.

---

## 🔌 Plugins

Plugins are TypeScript packages that hook into OpenClaw's runtime (heartbeat, messages, etc.).

**Available plugins:**

| Plugin | Description |
|--------|-------------|
| [billing-monitor](plugins/billing-monitor/) | Monitors API billing health, alerts on 402/401 errors |

### Install a plugin

```bash
openclaw plugin install @ai-pa/billing-monitor
```

Or manually:

```bash
cp -r plugins/billing-monitor /opt/ocana/openclaw/plugins/
openclaw gateway restart
```

Then configure in `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "ai-pa-billing-monitor": {
        "enabled": true,
        "config": {
          "adminPhone": "+1XXXXXXXXXX",
          "checkInterval": 60
        }
      }
    }
  }
}
```

---

## Contributing

1. Skills go in `skills/<skill-name>/` with a `SKILL.md`
2. Plugins go in `plugins/<plugin-name>/` with `package.json`, `openclaw.plugin.json`, and `index.ts`
3. Update this README with your addition
