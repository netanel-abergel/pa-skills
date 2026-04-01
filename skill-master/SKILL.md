---
name: skill-master
description: "Meta-skill for skill selection and routing. Use this skill FIRST when you are unsure which skill to use for a task. Provides a decision tree, keyword triggers, and guidance on combining multiple skills for complex workflows. Also use when onboarding to understand the full skill library."
---

# Skill Master

The routing layer. Use this to figure out which skill(s) to use before acting.

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
| "this task will take long" / "run this in background" | spawn-subagent |

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
│   └─ Long-running task → spawn-subagent
│
└─ SELF-IMPROVEMENT
    ├─ Owner corrected me → self-learning
    ├─ Weekly performance review → pa-eval
    └─ Pattern analysis → self-learning + pa-eval
```

---

## Full Skill Library

| Skill | Category | Complexity | Best For |
|---|---|---|---|
| **ai-pa** | Coordination | Low | Finding PA contacts, group JIDs, coordination protocols |
| **billing-monitor** | Health | Low | Detecting and responding to API billing failures |
| **calendar-setup** | Setup | Medium | Full calendar connection wizard with write access |
| **meeting-scheduler** | Operations | Medium | End-to-end meeting coordination between owners |
| **monday-workspace** | Operations | Medium | monday.com account, GraphQL API, MCP server |
| **openclaw-email-orientation** | Setup | Medium | Gmail + Calendar auth and troubleshooting |
| **owner-briefing** | Operations | Low | Daily morning/evening summaries |
| **pa-eval** | Self-improvement | Medium | Performance scoring, feedback analysis |
| **pa-onboarding** | Setup | High | Full new agent setup from zero |
| **pa-status** | Health | Low | Network-wide health dashboard |
| **self-learning** | Self-improvement | Low | Logging and applying lessons from mistakes |
| **spawn-subagent** | Architecture | Medium | Delegating long/blocking tasks |
| **whatsapp-diagnostics** | Health | Medium | Debugging WhatsApp connectivity issues |

---

## Multi-Skill Workflows

Some tasks require combining skills in sequence:

### New PA Setup (full)
```
pa-onboarding → calendar-setup → openclaw-email-orientation → monday-workspace → ai-pa (add to directory)
```

### Morning Routine
```
owner-briefing → spawn-subagent (if it should run non-blocking)
```

### PA Network Health Check
```
pa-status → billing-monitor (for any flagged PAs) → whatsapp-diagnostics (for unresponsive ones)
```

### After a Mistake
```
self-learning (log it) → pa-eval (update score) → SOUL.md (update rule if pattern)
```

### Schedule a Meeting
```
ai-pa (find the other PA's contact) → meeting-scheduler (coordinate + book)
```

---

## Skill Complexity Guide

### Low complexity — run inline, no subagent needed
- ai-pa, billing-monitor, owner-briefing, pa-status, self-learning

### Medium complexity — consider subagent for heavy operations
- calendar-setup (OAuth flow), meeting-scheduler (multi-step), monday-workspace (bulk ops)

### High complexity — spawn subagent recommended
- pa-onboarding (20+ steps), pa-eval (full analysis), batch operations

---

## Model Guidance

Some skills work with any model. Others benefit from stronger reasoning:

| Skill | Minimum Model | Notes |
|---|---|---|
| ai-pa | Any | Simple lookup |
| billing-monitor | Any | Pattern matching |
| owner-briefing | Small–Medium | Summarization |
| whatsapp-diagnostics | Small–Medium | Decision tree |
| calendar-setup | Small–Medium | Step-by-step |
| meeting-scheduler | Medium | Scheduling logic |
| monday-workspace | Medium | API operations |
| pa-eval | Medium–Large | Analysis + scoring |
| self-learning | Medium–Large | Pattern detection |
| pa-onboarding | Medium | Multi-step workflow |
| pa-status | Any | Data aggregation |
| spawn-subagent | Any | Task delegation |

---

## Adding New Skills

When a new skill is added to the library:
1. Add a row to the **Full Skill Library** table
2. Add trigger phrases to **Quick Lookup**
3. Update the **Decision Tree** if needed
4. Add to any relevant **Multi-Skill Workflows**

Keep this file as the single source of truth for skill routing.

---

## Auto-Updated

This skill is updated automatically when new skills are added. See skill-scout for how new skills are discovered.

---

## Skills Added After Initial Release

| Skill | Category | Complexity | Best For |
|---|---|---|---|
| **git-backup** | Memory | Low | Backup workspace to GitHub — token discovery, auto-push |
| **whatsapp-group-memory** | Memory | Low | Per-WhatsApp-group context: decisions, people, topics per group |
| **skill-scout** | Discovery | Medium | Weekly web search for new skill ideas |

### New Trigger Phrases

| If the owner says... | Use skill |
|---|---|
| "save this" / "backup" / "push to git" | git-backup |
| "what was discussed in [group]" | whatsapp-group-memory |
| "what do you know about [group]" | whatsapp-group-memory |
| "find new skill ideas" / "what skills are trending" | skill-scout |

### New Multi-Skill Workflows

**After any group conversation:**
```
whatsapp-group-memory (log decisions/people) → git-backup (persist to GitHub)
```

**Weekly maintenance:**
```
whatsapp-group-memory (weekly digest per group) → owner-briefing (include group highlights) → git-backup
```

**Memory before context compaction:**
```
whatsapp-group-memory (flush group contexts) → git-backup (push everything)
```
