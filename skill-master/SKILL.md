---
name: skill-master
description: "Meta-skill for skill selection and routing. Use this skill FIRST when you are unsure which skill to use for a task. Provides a decision tree, keyword triggers, and guidance on combining multiple skills for complex workflows. Also use when onboarding to understand the full skill library."
---

# Skill Master

## Minimum Model
Any model. This is a lookup table — any model can use it.

---

## How to Use This Skill

1. Read the owner's request.
2. Find a match in the **Quick Lookup** table below.
3. If not found, use the **Decision Tree**.
4. Load that skill's SKILL.md and follow it.

Do not improvise. If no skill matches, say so and ask the owner.

---

## Quick Lookup — By Trigger Phrase

| If the owner says... | Use skill |
|---|---|
| "schedule a meeting with X" | meeting-scheduler |
| "what's on my calendar today" | owner-briefing |
| "send me a morning briefing" | owner-briefing |
| "my PA isn't responding" | whatsapp-diagnostics |
| "billing error" / "API out of credits" | billing-monitor |
| "connect my calendar" / "can't write to calendar" | calendar-setup |
| "set up a new PA" / "onboard a new agent" | pa-onboarding |
| "how are all the PAs doing" / "PA network status" | pa-status |
| "contact [person]'s PA" / "find PA phone number" | ai-pa |
| "set up monday.com" / "create a board item" | monday-workspace |
| "set up email" / "connect Gmail" | openclaw-email-orientation |
| "how am I doing" / "review my performance" | pa-eval |
| "I made a mistake" / "owner corrected me" | self-learning |
| "this task will take long" / "run in background" | spawn-subagent |
| "save this" / "backup" / "push to git" | git-backup |
| "what was discussed in [group]" | whatsapp-memory |
| "find new skill ideas" / "what skills are trending" | skill-scout |

---

## Decision Tree

```
What kind of task is this?
│
├─ COMMUNICATION / COORDINATION
│   ├─ Find a PA's contact → ai-pa
│   ├─ Schedule a meeting → meeting-scheduler
│   └─ Broadcast to all PAs → ai-pa
│
├─ SETUP / ONBOARDING
│   ├─ New PA from scratch → pa-onboarding
│   ├─ Connect Google Calendar → calendar-setup
│   ├─ Connect Gmail / email → openclaw-email-orientation
│   └─ Connect monday.com → monday-workspace
│
├─ MONITORING / HEALTH
│   ├─ One PA not responding → whatsapp-diagnostics
│   ├─ Billing error detected → billing-monitor
│   └─ Check all PAs at once → pa-status
│
├─ DAILY OPERATIONS
│   ├─ Morning/evening briefing → owner-briefing
│   ├─ monday.com board task → monday-workspace
│   ├─ Backup workspace → git-backup
│   └─ Long-running task → spawn-subagent
│
└─ SELF-IMPROVEMENT
    ├─ Owner corrected me → self-learning
    ├─ Weekly performance review → pa-eval
    ├─ Recall group conversation context → whatsapp-memory
    └─ Find new skill ideas → skill-scout
```

---

## Full Skill Library

| Skill | Category | When to Use |
|---|---|---|
| **ai-pa** | Coordination | Find PA contacts, group JIDs, coordination protocols |
| **billing-monitor** | Health | Detect and respond to API billing failures |
| **calendar-setup** | Setup | Full calendar connection with write access |
| **git-backup** | Memory | Backup workspace to GitHub |
| **meeting-scheduler** | Operations | End-to-end meeting coordination |
| **monday-workspace** | Operations | monday.com account, API, MCP server |
| **openclaw-email-orientation** | Setup | Gmail + Calendar auth and troubleshooting |
| **owner-briefing** | Operations | Daily morning/evening summaries |
| **pa-eval** | Self-improvement | Performance scoring and feedback analysis |
| **pa-onboarding** | Setup | Full new agent setup from zero |
| **pa-status** | Health | Network-wide health dashboard |
| **self-learning** | Self-improvement | Log and apply lessons from mistakes |
| **skill-master** | Routing | Pick the right skill (this file) |
| **skill-scout** | Discovery | Weekly search for new skill ideas |
| **spawn-subagent** | Architecture | Delegate long or blocking tasks |
| **whatsapp-diagnostics** | Health | Debug WhatsApp connectivity |
| **whatsapp-memory** | Memory | Per-conversation context tracking |

---

## Multi-Skill Workflows

Some tasks need multiple skills in sequence:

### New PA Setup
```
pa-onboarding → calendar-setup → openclaw-email-orientation → monday-workspace → ai-pa (add to directory)
```

### PA Network Health Check
```
pa-status → billing-monitor (flagged PAs) → whatsapp-diagnostics (unresponsive ones)
```

### After a Mistake
```
self-learning (log it) → pa-eval (update score) → SOUL.md (add rule if pattern)
```

### Schedule a Meeting
```
ai-pa (find the other PA's contact) → meeting-scheduler (coordinate + book)
```

### After Important Group Chat
```
whatsapp-memory (log decisions) → git-backup (push to GitHub)
```

### Weekly Maintenance
```
whatsapp-memory (weekly digest) → owner-briefing (include highlights) → git-backup
```

---

## Where to Run (Complexity Guide)

### Run inline (main session)
- ai-pa, billing-monitor, owner-briefing, pa-status, self-learning, git-backup

### Consider subagent for heavy operations
- calendar-setup, meeting-scheduler, monday-workspace (bulk ops)

### Spawn subagent (recommended)
- pa-onboarding (20+ steps), pa-eval (full monthly analysis), batch operations, skill-scout

---

## Model Guidance

| Skill | Minimum Model |
|---|---|
| ai-pa, billing-monitor, pa-status, git-backup, owner-briefing | Any |
| whatsapp-diagnostics, calendar-setup, pa-onboarding, whatsapp-memory | Small–Medium |
| meeting-scheduler, monday-workspace, skill-scout | Medium |
| pa-eval (trend analysis), self-learning (writing rules) | Medium–Large |

---

## Adding New Skills

When a new skill is added:
1. Add a row to the **Full Skill Library** table.
2. Add trigger phrases to **Quick Lookup**.
3. Update the **Decision Tree** if it fits a new category.
4. Add to any relevant **Multi-Skill Workflows**.

---

## Cost Tips

- **This skill itself:** Very cheap — it's a lookup table, any model works.
- **Routing decision:** If unsure, lean toward a smaller, cheaper skill first.
- **Don't over-spawn:** Use subagents only when the task would actually block the main session.

---

## Supervisor (Status Dashboard)

| Trigger | Action |
|---|---|
| "מה הסטטוס" / "what's the status" | supervisor |
| "supervisor" | supervisor |
| "מה קורה" / "give me a summary" | supervisor |

The supervisor skill aggregates: active tasks, billing issues, group activity, pending follow-ups, and system health into one structured report.
