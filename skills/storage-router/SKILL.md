---
name: storage-router
description: "Decide where to save any piece of information — monday.com, local file, or MEMORY.md. Use this skill before saving anything to ensure the right destination. Prevents local clutter and ensures Netanel can access all relevant content in monday.com."
---

# Storage Router

Before saving anything, route it to the correct destination.

---

## Decision Table

| Content Type | Destination | Notes |
|---|---|---|
| Competitor research | monday.com — Competitive Analysis doc | Builders CoWORK workspace |
| Product briefs, strategy docs | monday.com — relevant doc | Builders CoWORK workspace |
| Meeting notes | monday.com — Notetaker / item update | |
| Project tasks / tracking | monday.com — board item | |
| PA rules & preferences | MEMORY.md | Long-term only, distilled |
| Lessons learned | MEMORY.md | After 2+ repetitions |
| Daily event log | memory/YYYY-MM-DD.md | Raw log, not curated |
| WhatsApp conversation context | memory/whatsapp/groups/ or dms/ | Per-conversation, local |
| Cron state / job state | local JSON (data/ or inbox/) | Runtime state only |
| PA contact list | PA_LIST.md (local) | Source of truth for PA sync |
| Config / credentials | local only, never monday | Security |
| Skill files | workspace/skills/ | Never monday |

---

## Rules

### ALWAYS → monday.com
- Research (competitors, market, technology)
- Documents Netanel needs to access or share
- Project tracking, tasks, milestones
- Meeting summaries
- GTM, product, strategy content

### ALWAYS → local
- Runtime state (cron jobs, inbox, heartbeat state)
- WhatsApp memory (per-conversation context)
- Credentials and config
- PA directory (PA_LIST.md)

### ALWAYS → MEMORY.md
- Netanel preferences (after confirmed 2+ times)
- Behavioral rules (after a correction)
- Key contacts and relationships
- System facts (calendar auth, server details)

### NEVER
- ❌ Save research/docs to local files
- ❌ Save credentials or config to monday.com
- ❌ Save WhatsApp context to monday.com
- ❌ Duplicate content in both local and monday

---

## monday.com Workspace Map

**Workspace:** Builders CoWORK (ID: 14880329)
**Structure Index Doc:** 39993682 (always check here for latest IDs)

| Content | Folder | Board/Doc ID |
|---|---|---|
| Competitor analysis | 📁 Research (20077300) | Board: 18406632346 / Doc: 39808656 |
| Market research | 📁 Research (20077300) | Board: 18406632334 |
| Technology deep dives | 📁 Research (20077300) | Per-tool board (see index) |
| Product brief | 📁 Product (20077301) | Board: 18406632301 / Doc: 39808645 |
| MVP planning | 📁 Product (20077301) | Board: 18406632217 |
| GTM strategy | 📁 GTM (20077298) | Board: 18406632223 |
| PA Rollout tracking | 📁 Operations (20077299) | Board: 18407159006 |
| Skills guide | 📁 Operations (20077299) | Board: 18407110746 |

> For full index with all IDs: read doc 39993682 in monday.com before saving anything new.

---

## How to Use

Before saving any file or content, ask:

1. **Will Netanel need to access or share this?** → monday.com
2. **Is this runtime/operational state?** → local
3. **Is this a rule or preference I've confirmed multiple times?** → MEMORY.md
4. **Is this a daily event log?** → memory/YYYY-MM-DD.md

When in doubt → monday.com for content, local for state.

---

## Trigger Phrases
- "שמרי את זה"
- "save this"
- "תתעדי"
- "document this"
- Before writing any file with research, analysis, or docs
