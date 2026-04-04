---
name: task-tracker
description: "Manage multi-step tasks in the monday.com Task Tracker board. Use when: a task has multiple steps, spans multiple sessions, involves subagents, or could block the main session. Creates tickets with full context so tasks survive session restarts."
---

# Task Tracker Skill

Ticket-based task management. Every multi-step task gets a board item — so context survives session restarts.

---

## Load Local Context
```bash
CONTEXT_FILE="/opt/ocana/openclaw/workspace/skills/task-tracker/.context"
[ -f "$CONTEXT_FILE" ] && source "$CONTEXT_FILE"
# Provides: $BOARD_ID, $GROUP_ACTIVE, $GROUP_BLOCKED, $GROUP_DONE
```

---

## When to Create a Ticket

Create a task-tracker item when:
- Task has 3+ steps
- Task involves a subagent
- Task will take >5 minutes
- Task could resume next session
- Owner asks to track something

Do NOT create a ticket for:
- Simple one-shot answers
- Lookups / searches
- Quick replies

---

## Ticket Lifecycle

```
NEW → open item in 🔴 Active group
IN_PROGRESS → update "Context & Steps" with current state
BLOCKED → move to 🟡 Blocked, fill "Blocked By"
DONE → move to ✅ Done
```

---

## Create a Ticket

```bash
# Via monday-api-mcp__create_item
boardId: $BOARD_ID
groupId: $GROUP_ACTIVE
name: "<task name>"
columnValues: {
  "status": {"label": "Working on it"},
  "goal_why": "<which Active Goal this connects to>",
  "context_steps": "<what the task is, steps planned, decisions made>",
  "due": {"date": "YYYY-MM-DD"}  # if known
}
```

---

## Update a Ticket

After each session where progress was made:
```bash
# Update "Context & Steps" with:
# - What was done
# - What's next
# - Any decisions made
# - Subagent status if relevant
```

---

## Close a Ticket

When done:
1. Move item to ✅ Done group
2. Add final update: what was delivered, any learnings
3. If significant → add to daily memory file

---

## Integration with Other Skills

- **spawn-subagent:** Create ticket before spawning. Log `IN_PROGRESS → subagent` in ticket.
- **skill-master:** Check if task needs a ticket before starting (3+ steps = yes).
- **audit-log:** Log ticket creation as an action.
- **storage-router:** Final deliverables go to monday.com (not local).

---

## Trigger Phrases
- "תעקבי על זה"
- "track this"
- "משימה מורכבת"
- "כמה שלבים"
- "תפתחי ticket"
