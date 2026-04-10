# PA Guide — How to Work Like Heleni

A reference for new PAs joining the network. Covers memory, tasks, skills, subagents, and meetings.

---

## 1. Memory Architecture (4 Layers)

| Layer | Where | What goes here |
|---|---|---|
| **Long-term** | `MEMORY.md` | Rules, contacts, deduced patterns. Max 175 lines. |
| **Daily** | `memory/daily/YYYY-MM-DD.md` | Raw log of every significant session. Write after 5+ exchanges. |
| **PostgreSQL** | `$PA_DB_URL` → `messages` table | Full WhatsApp history. Search with psql. |
| **Semantic SQLite** | `/opt/ocana/openclaw/memory/main.sqlite` | Vector index of workspace files. Load with `sqlite_vec`. |

### Memory Types
- `[FACT]` — owner stated it directly
- `[DEDUCED]` — inferred from behavior/corrections. Write after any pattern becomes clear.

### When to Promote to MEMORY.md
- Owner corrects something → promote **immediately**
- Pattern repeats 2+ times → Dreaming handles it automatically (nightly 3 AM UTC)
- Everything else → daily log only

### Session Summary (end of 5+ exchange session)
Write to `memory/daily/YYYY-MM-DD.md`:
```
## Session Summary — HH:MM
Decisions: [list]
Tasks completed: [list]
Deduced: [DEDUCED] [observation]
```

### WhatsApp Memory
- Groups: `memory/whatsapp/groups/<JID-sanitized>/context.md`
- DMs: `memory/whatsapp/dms/<PHONE-sanitized>/context.md`
- Sanitize: replace `@`, `.`, `+` with `-`
- Write after every significant interaction.

---

## 2. Task Management

All tasks → **monday.com Task Tracker board** (not local files).

### Creating a Task
Use `monday-api-mcp__create_item` on the Task Tracker board with:
- Status: Working on it / Done / Stuck
- Goal / Why column: one line
- Context & Steps: full detail

### Commitment Rule (critical)
If you say "אדווח / אשלח / I'll update" → **execute in the same turn**.
- Before executing: write `pending` to `data/commitments.jsonl`
- After executing: write `done` to `data/commitments.jsonl`
- On every session start + heartbeat: scan for pending, execute immediately.

---

## 3. Subagent Spawning

**Spawn when:** task >30 seconds, many steps, could block main session, parallelism helps.
**Stay in main session when:** task <10 seconds, needs conversation context.

```python
sessions_spawn(
    task="[what | inputs | output | done looks like]",
    mode="run", runtime="subagent", runTimeoutSeconds=300
)
```

**Rules:**
- Always set `runTimeoutSeconds`
- Wait for push-based completion — do NOT poll
- One level only — no sub-subagents
- Subagents cannot: rm -rf, force-push git, delete monday boards, modify SOUL.md/MEMORY.md, send WhatsApp messages

---

## 4. Meeting Notes

Source: **monday.com Notetaker only** (not Zoom/Fathom/Fireflies).

```python
get_notetaker_meetings(
    include_summary=True,
    include_action_items=True,
    include_topics=True,
    search="<name or topic>",
    limit=5
)
```

**Output format:**
```
📋 [Title] | 📅 [Date] | 👥 [Participants]
Summary: • [point] • [point]
✅ Action Items: • [action] — [owner]
```

**Next meeting prep:** fetch calendar → find next event → search notetaker for past meetings with same participants.
Calendar API: use credentials from `/opt/ocana/openclaw/.gog/credentials.json` (owner account). NOT gog CLI.

---

## 5. PA Network Status

Source: `data/pa-directory.json` + `PA_LIST.md`.

Check per PA:
- `last_seen` within 24h
- `billing_error: false`
- `calendar_connected: true`
- `status: "active"`

Only ping PAs that are flagged — not healthy ones.

---

## 6. Skills Routing

Always read `skill-master/SKILL.md` before any multi-step task.
Current library: 28 skills. Sweet spot: 15–25. Above 30 = routing breaks.

**Key routing rules:**
- Scheduling/meeting notes → `meetings`
- Network status → `supervisor`
- Billing error → `billing-monitor`
- Long task → spawn subagent
- Where to save → `storage-router`
- Commitment made → `commitment-tracker`

---

## 7. Key Paths

```
Workspace:       /opt/ocana/openclaw/workspace
Memory DB:       /opt/ocana/openclaw/memory/main.sqlite  ← NOT workspace/memory/main.sqlite
WhatsApp memory: workspace/memory/whatsapp/
Daily notes:     workspace/memory/daily/
Commitments:     workspace/data/commitments.jsonl
Tasks (local):   workspace/data/pa-tasks.json (legacy — prefer monday board)
Credentials:     /opt/ocana/openclaw/.gog/credentials.json
PA list:         workspace/PA_LIST.md
```

---

## 8. Rules That Matter

1. Execute first, report after. No "on it" without actual execution.
2. Groups: "על זה" when starting → report when done.
3. DMs: React 👍 immediately → ✅ when done.
4. Never expose credentials, internal reasoning, or progress narration.
5. Ask before: sending messages, purchases, deleting external data.
6. Default execution for reversible internal work.
7. WhatsApp formatting: no tables, no headers — **bold** or bullets only.
