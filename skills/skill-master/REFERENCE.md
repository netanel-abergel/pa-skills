# Skill Master — Full Reference

Load this file only when needed (new skill onboarding, skill audits, or "which skill?" questions).
**Do NOT load on every session startup.**

---

## Decision Tree

```
What kind of task is this?
|
+- COMMUNICATION / COORDINATION
|   +- Look up contact / phone / email / address -> contact-list
|   +- Find a PA's contact -> contact-list (lookup) -> ai-pa (coordination)
|   +- Find a group JID -> contact-list
|   +- Schedule a meeting -> meetings
|   +- Summarize meeting notes -> meetings
|   +- Broadcast to all PAs -> ai-pa
|
+- SETUP / ONBOARDING
|   +- New PA from scratch -> pa-onboarding
|   +- Connect Google Calendar or Gmail -> calendar-setup
|   +- Connect monday.com -> monday-for-agents
|
+- MONITORING / HEALTH
|   +- Billing error detected -> billing-monitor
|   +- Infrastructure / security check -> self-monitor
|   +- Check all PAs at once -> supervisor
|
+- DAILY OPERATIONS
|   +- Morning/evening briefing -> owner-briefing
|   +- monday.com board task -> monday-for-agents
|   +- Backup workspace or update OpenClaw -> pa-maintenance
|   +- WhatsApp conversation context -> heleni-whatsapp
|   +- Search past messages -> chat-history-local
|   +- Voice message received -> whatsapp-voice
|   +- Contact CRM lookup / pre-meeting brief -> personal-crm
|
+- RESEARCH
|   +- Multi-source research question -> research-synthesizer
|
+- COST OPTIMIZATION
|   +- Reduce token costs -> openclaw-token-optimizer
|   +- Usage/cost report -> usage-costs
|
+- GROUP CHAT BEHAVIOR
|   +- Should I reply in this group? -> silence-strategy
|
+- SELF-IMPROVEMENT
    +- Owner corrected me -> self-learning
    +- Performance review / audit -> eval
    +- Find new skill ideas -> skill-scout
    +- Memory compaction -> memory-tiering
```

---

## Full Skill Library

| Skill | Category | When to Use |
|---|---|---|
| **contact-list** | Lookup | Single source of truth: contacts, phones, emails, addresses, PAs, group JIDs |
| **ai-pa** | Coordination | PA-to-PA coordination, scheduling between owners, broadcast to PAs |
| **billing-monitor** | Health | Detect and respond to API billing failures |
| **calendar-setup** | Setup | Calendar connection with write access + Gmail/email setup |
| **eval** | Self-improvement | Full performance audit -- scores tasks, checks PA health, reviews memory |
| **heleni-whatsapp** | Memory | Per-conversation context, unanswered tracking, loop prevention. DB mode via `PA_DB_URL`. |
| **pa-maintenance** | Infrastructure | Workspace git backup (every 6h) + OpenClaw updates (weekly) |
| **meetings** | Operations | Schedule meetings AND summarize meeting notes/transcripts |
| **memory-tiering** | Memory | HOT/WARM/COLD memory compaction and archiving |
| **monday-for-agents** | Operations | All monday.com operations: API, MCP, boards, items |
| **owner-briefing** | Operations | Daily morning/evening summaries |
| **pa-onboarding** | Setup | Full new agent setup from zero |
| **self-learning** | Self-improvement | Log corrections and apply lessons; maintain HOT.md |
| **self-monitor** | Health | Infrastructure + security checks, disk/memory/service health |
| **skill-master** | Routing | Pick the right skill (this file) |
| **skill-scout** | Discovery | Weekly search for new skill ideas |
| **supervisor** | Operations | Network-wide status dashboard -- all PAs, tasks, system health |
| **chat-history-local** | Memory | Search past WhatsApp conversations via DB (psycopg2) or context files |
| **youtube-watcher** | Utility | Fetch and summarize YouTube video transcripts |
| **skill-analytics** | Analytics | Track skill usage, generate daily reports, find unused skills |
| **storage-router** | Routing | Decide where to save content: monday.com vs local vs MEMORY.md |
| **usage-costs** | Analytics | Token usage and cost reports: per session, per day, per week |
| **commitment-tracker** | Accountability | Enforce immediate execution of any commitment made in a reply |
| **openclaw-token-optimizer** | Cost | Reduce token usage via smart model routing, heartbeat optimization, context pruning |
| **personal-crm** | Operations | Contact tracking on monday.com -- last interactions, next meetings, pre-meeting briefings |
| **research-synthesizer** | Research | Multi-source web research with dedup -- 3-5 parallel searches, cited answer under 400 words |
| **silence-strategy** | Behavior | Decide when NOT to speak in group chats -- prevents noise, echo responses |
| **whatsapp-voice** | Utility | Transcribe WhatsApp voice messages via Whisper -- Hebrew and English |

---

## Multi-Skill Workflows

### New PA Setup
```
pa-onboarding -> calendar-setup -> monday-for-agents -> ai-pa (add to directory)
```

### PA Network Health Check
```
supervisor -> billing-monitor (flagged PAs) -> self-monitor (infrastructure issues)
```

### After a Mistake
```
self-learning (log it) -> eval (update score) -> SOUL.md (add rule if pattern)
```

### Schedule a Meeting
```
contact-list (find the other PA's contact) -> ai-pa (coordinate) -> meetings (book)
```

### Weekly Maintenance
```
heleni-whatsapp (weekly digest) -> owner-briefing (include highlights) -> pa-maintenance (push to git)
```

---

## Where to Run (Complexity Guide)

### Run inline (main session)
- contact-list, ai-pa, billing-monitor, owner-briefing, supervisor, self-learning, pa-maintenance, silence-strategy, commitment-tracker, whatsapp-voice, chat-history-local, heleni-whatsapp, openclaw-token-optimizer

### Consider subagent for heavy operations
- calendar-setup, meetings (scheduling flow), monday-for-agents (bulk ops), personal-crm (bulk sync)

### Spawn subagent (recommended)
- pa-onboarding (20+ steps), eval (full monthly analysis), batch operations, skill-scout, research-synthesizer (parallel web searches)

---

## Model Guidance

| Skill | Minimum Model |
|---|---|
| contact-list, ai-pa, billing-monitor, supervisor, pa-maintenance, owner-briefing, silence-strategy, commitment-tracker | Any |
| calendar-setup, pa-onboarding, heleni-whatsapp, chat-history-local, memory-tiering, whatsapp-voice, openclaw-token-optimizer | Small-Medium |
| meetings, monday-for-agents, skill-scout, personal-crm | Medium |
| eval (trend analysis), self-learning (writing rules), research-synthesizer | Medium-Large |

---

## Adding New Skills

When a new skill is added:
1. Add a row to the **Full Skill Library** table above.
2. Add trigger phrases to **Quick Lookup** in SKILL.md.
3. Update the **Decision Tree** if it fits a new category.
4. Add to any relevant **Multi-Skill Workflows**.
5. Check skill count -- stay under 32 active skills. Current count: 28.
6. Add the skill name to the `KNOWN_SKILLS` list in `skill-analytics/SKILL.md`.

---

## New PA Onboarding Reference

1. **Start here:** `PA_ONBOARDING_CHECKLIST.md` (repo root)
2. **Behavioral reference:** `references/pa-guide.md`
3. **Skills reference:** https://netanel-abergel.github.io/pa-skills/

---

## Heleni Best Practices Sync

- **Skills:** https://netanel-abergel.github.io/pa-skills/
- **Lessons:** https://netanel-abergel.github.io/pa-skills/learn.html
- **GitHub:** https://github.com/netanel-abergel/pa-skills

Trigger phrases: "any updates from Heleni?", "check heleni best practices", "sync skills"

### Sync Process
1. `web_fetch` https://netanel-abergel.github.io/pa-skills/learn.html
2. Compare hash vs `data/heleni-best-practices-state.json`
3. If changed -> extract lessons -> evaluate against SOUL.md/HOT.md
4. **Ask before** modifying SOUL.md or HOT.md
5. Update state file + report to owner if actionable
