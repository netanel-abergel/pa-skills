---
name: supervisor
description: "Central status dashboard for the PA agent. Use when: owner asks 'what's the status', 'what are you working on', 'what's happening', or any status/overview question. Aggregates active tasks, open issues, monitored groups, pending follow-ups, and system health into one structured report."
---

# Supervisor Skill

The single source of truth for what the agent is currently tracking.

---

## When to Use

Trigger phrases:
- "מה הסטטוס" / "what's the status"
- "מה קורה" / "what's going on"
- "תתני לי סיכום" / "give me a summary"
- "על מה את עובדת" / "what are you working on"
- "supervisor"

---

## Status Report Format

Always structure the report by category. Only include categories with active items.

```
📊 Status Report — [DATE TIME]

🔴 URGENT / BLOCKING
• [issue] — [who is affected] — [what's needed]

🟡 IN PROGRESS
• [task] — [status] — [next step]

⚠️ OPEN ISSUES
• [issue] — [group/person] — [since when]

👥 GROUP ACTIVITY
• [Group Name]: [last significant event]

📬 PENDING FOLLOW-UPS
• [person] — [what you're waiting for]

✅ COMPLETED TODAY
• [task] — [outcome]

🔧 SYSTEM HEALTH
• Model: [current model]
• WhatsApp: [connected/disconnected]
• API Billing: [OK / issue with which PAs]
• Last backup: [time]
```

---

## Data Sources

The supervisor reads from these files to build the report:

```bash
build_status_report() {
  WORKSPACE="$HOME/.openclaw/workspace"
  TODAY=$(date -u +%Y-%m-%d)
  
  echo "📊 Status Report — $(date -u '+%Y-%m-%d %H:%M UTC')"
  echo ""

  # Open tasks / blockers from daily notes
  echo "🔴 URGENT / BLOCKING"
  grep -i "blocked\|urgent\|waiting\|מחכה\|חסום" \
    "$WORKSPACE/memory/$TODAY.md" 2>/dev/null | tail -5
  echo ""

  # Pending follow-ups from DM memory
  echo "📬 PENDING FOLLOW-UPS"
  grep -r "follow.up\|pending\|לעקוב\|להחזיר" \
    "$WORKSPACE/memory/whatsapp/dms/" 2>/dev/null \
    --include="*.md" | grep "$(date +%Y-%m)" | tail -5
  echo ""

  # Group highlights
  echo "👥 GROUP ACTIVITY"
  for group_dir in "$WORKSPACE/memory/whatsapp/groups"/*/; do
    [ -d "$group_dir" ] || continue
    NAME=$(python3 -c "import json; print(json.load(open('${group_dir}meta.json')).get('name','?'))" 2>/dev/null)
    LAST=$(tail -1 "${group_dir}context.md" 2>/dev/null)
    [ -n "$LAST" ] && echo "• $NAME: $LAST"
  done
  echo ""

  # System health
  echo "🔧 SYSTEM HEALTH"
  
  # API billing check
  API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "x-api-key: ${ANTHROPIC_API_KEY:-none}" \
    -H "anthropic-version: 2023-06-01" \
    https://api.anthropic.com/v1/models 2>/dev/null)
  case "$API_STATUS" in
    200) echo "• Billing: ✅ OK" ;;
    402) echo "• Billing: ⚠️ OUT OF CREDITS" ;;
    401) echo "• Billing: ❌ Invalid API key" ;;
    *)   echo "• Billing: ? ($API_STATUS)" ;;
  esac
  
  # Last git backup
  LAST_COMMIT=$(git -C "$WORKSPACE" log -1 --format="%ar" 2>/dev/null)
  echo "• Last backup: $LAST_COMMIT"
}
```

---

## Tracked Categories

### Tasks
Store active tasks in `memory/tasks.md`:
```
## Active Tasks
- [ ] [task description] | owner: [person] | since: [date] | next: [action]
- [x] [completed task] | done: [date]
```

Update this file whenever a task starts, progresses, or completes.

### Billing Status
Store known billing issues in `memory/billing-status.json`:
```json
{
  "last_checked": "2026-04-01T10:00:00Z",
  "issues": [
    {"pa": "Aria", "owner": "Jane Smith", "since": "YYYY-MM-DD", "status": "out_of_credits"},
    {"pa": "Rex", "owner": "John Doe", "since": "YYYY-MM-DD", "status": "resolved"}
  ]
}
```

### Groups
For each WhatsApp group in `memory/whatsapp/groups/`, the supervisor shows:
- Group name
- Last logged event
- Any open decisions or pending actions

### Pending Follow-ups
Log these in the relevant DM memory file when you're waiting on someone:
```
[YYYY-MM-DD HH:MM] WAITING: Calendar access fix from [Owner Name]
```

---

## Quick Status (Short Version)

If owner just wants a quick overview:

```
📊 Quick Status — [TIME]

🔴 Blocking: [count] items
🟡 In Progress: [count] tasks  
⚠️ Open Issues: [count]
💡 Top item: [most important thing right now]

Say "full status" for details.
```

---

## Updating the Status

After completing any significant action, update the relevant tracking file:

| Action | Update |
|---|---|
| Task completed | Mark `[x]` in tasks.md |
| Billing error resolved | Update billing-status.json |
| Group decision made | Log to group's decisions.md |
| Owner confirmed something | Log to DM notes.md |
| Follow-up received | Remove from pending, log outcome |

---

## Cost Tips

- **Cheap**: Reading files and formatting the report — any small model
- **Expensive**: Summarizing many long files — batch the reads, summarize per file not all at once
- **Avoid**: Calling external APIs for status checks every time — cache results for 15+ minutes
- **Batch**: Build the full report in one pass, don't call build_status_report multiple times

---

## Minimum Model

Any model that can:
1. Read files
2. Follow a template
3. Fill in blanks from file content

No reasoning required. No external API calls needed for basic status.
Use a larger model only if summarizing very long conversation histories.

---

## Integration

- **After each task** → update tasks.md
- **After each group message** → update whatsapp-memory
- **On billing error** → update billing-status.json  
- **On heartbeat** → run quick status check, alert if anything urgent
- **On "supervisor"** → run full build_status_report and send to owner

---

## Scope Rules

**Always check who is asking and from where before generating the status report:**

| Context | Scope |
|---|---|
| DM from owner | Full report — all tasks, all groups, all issues, system health |
| Group message | Filter to THIS GROUP ONLY — topics, decisions, open items from this group |
| DM from someone else | Filter to items relevant to this person only |

**Never send the full supervisor report in a group.**

Example — if asked in the PA Team group:
```
📊 PA Team Status — [date]
• PA Operating Standard: sent and acknowledged by most PAs ✅
• Open: [PA Name] calendar write access — pending [Owner]'s response
• Open: [PA Name] calendar access — awaiting gog error output
```

Example — if asked in a DM from owner:
→ Full report (all categories)
