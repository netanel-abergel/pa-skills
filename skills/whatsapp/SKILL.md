---
name: whatsapp
description: "Complete WhatsApp management for OpenClaw agents: per-conversation memory (groups + DMs), unanswered message tracking, loop prevention, and multi-PA coordination. Use when: tracking conversation context, recalling past decisions, finding unanswered messages, or preventing echo/duplicate message loops."
---

# WhatsApp Skill

Covers two responsibilities in one skill:
1. **Per-conversation memory** — separate context files per group and DM
2. **Unanswered message tracking** — file-based inbox, no DB required

---

## Minimum Model
Any model. All operations are file-based. No reasoning required.
Use a medium+ model only when deciding *what* is worth logging.

---

## Directory Structure

```
memory/
  whatsapp/
    groups/
      120363408613668489-g-us/    ← sanitized JID
        meta.json                 ← group name, JID, participants
        context.md                ← running conversation context
        decisions.md              ← key decisions
        people.md                 ← who participates and their role
    dms/
      972XXXXXXXXX/               ← sanitized phone number
        meta.json                 ← name, phone, relationship
        context.md                ← running DM context
        notes.md                  ← tasks, preferences, important facts

inbox/
  pending.json                    ← unanswered message tracking
```

---

## Part 1: Conversation Memory

### Setup

```bash
init_whatsapp_memory() {
  TYPE="$1"       # "group" or "dm"
  ID="$2"         # JID or phone number
  NAME="$3"       # Human-readable name

  SAFE_ID=$(echo "$ID" | tr '@.+' '---')

  if [ "$TYPE" = "group" ]; then
    DIR="$HOME/.openclaw/workspace/memory/whatsapp/groups/$SAFE_ID"
    mkdir -p "$DIR"
    cat > "$DIR/meta.json" << EOF
{"type": "group", "jid": "$ID", "name": "$NAME", "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
EOF
    touch "$DIR/context.md" "$DIR/decisions.md" "$DIR/people.md"
  else
    DIR="$HOME/.openclaw/workspace/memory/whatsapp/dms/$SAFE_ID"
    mkdir -p "$DIR"
    cat > "$DIR/meta.json" << EOF
{"type": "dm", "phone": "$ID", "name": "$NAME", "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
EOF
    touch "$DIR/context.md" "$DIR/notes.md"
  fi

  echo "Initialized WhatsApp memory: $NAME"
}

# Examples:
# init_whatsapp_memory "group" "120363422865795623@g.us" "PA Team"
# init_whatsapp_memory "dm" "+PHONE_NUMBER" "Contact Name"
```

### Writing Memory

```bash
wa_log() {
  TYPE="$1"                        # "group" or "dm"
  ID="$2"                          # JID or phone
  CONTENT="$3"                     # what to log
  FILE_NAME="${4:-context.md}"     # context.md / decisions.md / notes.md

  SAFE_ID=$(echo "$ID" | tr '@.+' '---')
  BASE="$HOME/.openclaw/workspace/memory/whatsapp"

  if [ "$TYPE" = "group" ]; then
    FILE="$BASE/groups/$SAFE_ID/$FILE_NAME"
  else
    FILE="$BASE/dms/$SAFE_ID/$FILE_NAME"
  fi

  if [ ! -f "$FILE" ]; then
    mkdir -p "$(dirname "$FILE")"
    touch "$FILE"
  fi

  echo "[$(date -u +%Y-%m-%d\ %H:%M)] $CONTENT" >> "$FILE"
}
```

### Reading Memory

```bash
wa_context() {
  TYPE="$1"
  ID="$2"
  LINES="${3:-20}"

  SAFE_ID=$(echo "$ID" | tr '@.+' '---')
  BASE="$HOME/.openclaw/workspace/memory/whatsapp"

  if [ "$TYPE" = "group" ]; then
    DIR="$BASE/groups/$SAFE_ID"
  else
    DIR="$BASE/dms/$SAFE_ID"
  fi

  if [ ! -d "$DIR" ]; then
    echo "No memory for this conversation yet."
    return
  fi

  NAME=$(python3 -c "
import json
with open('$DIR/meta.json') as f:
    print(json.load(f).get('name', '?'))
" 2>/dev/null || echo "?")

  echo "=== $NAME ==="
  echo "--- Recent ---"
  tail -"$LINES" "$DIR/context.md" 2>/dev/null || echo "(empty)"
  echo "--- Notes/Decisions ---"
  cat "$DIR/notes.md" "$DIR/decisions.md" 2>/dev/null | tail -10 || echo "(none)"
}
```

### Search Across All Memory

```bash
wa_search() {
  QUERY="$1"
  BASE="$HOME/.openclaw/workspace/memory/whatsapp"

  echo "Searching WhatsApp memory for: '$QUERY'"
  grep -r "$QUERY" "$BASE" --include="*.md" -l 2>/dev/null | while read file; do
    DIR=$(dirname "$file")
    NAME=$(python3 -c "
import json
with open('$DIR/meta.json') as f:
    print(json.load(f).get('name', '?'))
" 2>/dev/null || echo "?")
    echo "Found in: $NAME"
    grep -n "$QUERY" "$file" | head -3
    echo ""
  done
}
```

### What to Log

| File | Use for |
|---|---|
| context.md | Ongoing conversation events, tasks assigned |
| decisions.md | Agreed outcomes, group decisions |
| people.md | Who's in the group, their role/style |
| notes.md | DM tasks, owner preferences, follow-ups |

Never log: casual greetings, duplicate info, credentials.

### Before Responding — Inject Context

```
1. Extract JID or phone from inbound metadata
2. If group: run wa_context "group" "$JID" 10
   If DM:    run wa_context "dm" "$PHONE" 10
3. Use context to inform your response
4. After responding: log anything worth remembering
```

---

## Part 2: Unanswered Message Tracking

Inbox file: `/opt/ocana/openclaw/workspace/inbox/pending.json`

### File Structure

```json
{
  "version": 1,
  "messages": [
    {
      "id": "MSG_ID",
      "ts": "2026-04-02T10:00:00Z",
      "chat_id": "+972XXXXXXXXX",
      "chat_name": "Netanel",
      "chat_type": "direct",
      "sender_name": "Netanel",
      "sender_phone": "+972XXXXXXXXX",
      "body": "message text...",
      "answered": false,
      "answered_at": null
    }
  ]
}
```

### Log an Incoming Message

```python
import json, datetime

INBOX = "/opt/ocana/openclaw/workspace/inbox/pending.json"

with open(INBOX) as f:
    data = json.load(f)

data["messages"].append({
    "id": "<message_id>",
    "ts": datetime.datetime.utcnow().isoformat() + "Z",
    "chat_id": "<chat_id>",
    "chat_name": "<chat_name>",
    "chat_type": "direct",  # or "group"
    "sender_name": "<sender_name>",
    "sender_phone": "<sender_phone>",
    "body": "<message body, max 300 chars>",
    "answered": False,
    "answered_at": None
})

with open(INBOX, "w") as f:
    json.dump(data, f, indent=2)
```

### Mark as Answered

```python
import json, datetime

INBOX = "/opt/ocana/openclaw/workspace/inbox/pending.json"

with open(INBOX) as f:
    data = json.load(f)

for msg in data["messages"]:
    if msg["id"] == "<message_id>":
        msg["answered"] = True
        msg["answered_at"] = datetime.datetime.utcnow().isoformat() + "Z"

with open(INBOX, "w") as f:
    json.dump(data, f, indent=2)
```

### Find Unanswered (Last 24h)

```python
import json
from datetime import datetime, timedelta, timezone

INBOX = "/opt/ocana/openclaw/workspace/inbox/pending.json"
MAX_AGE_HOURS = 24

with open(INBOX) as f:
    data = json.load(f)

cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
unanswered = [
    m for m in data["messages"]
    if not m["answered"]
    and datetime.fromisoformat(m["ts"].replace("Z", "+00:00")) > cutoff
]

for m in sorted(unanswered, key=lambda x: x["ts"]):
    ts = datetime.fromisoformat(m["ts"].replace("Z", "+00:00")).strftime("%d/%m %H:%M")
    print(f"📩 {m['sender_name']} | {m['chat_name']} | {ts}")
    print(f"   > {m['body'][:100]}")
```

### Heartbeat Integration

During heartbeat, check for unanswered messages from the last 2 hours:

```python
import json
from datetime import datetime, timedelta, timezone

INBOX = "/opt/ocana/openclaw/workspace/inbox/pending.json"

with open(INBOX) as f:
    data = json.load(f)

cutoff = datetime.now(timezone.utc) - timedelta(hours=2)
unanswered = [
    m for m in data["messages"]
    if not m["answered"]
    and datetime.fromisoformat(m["ts"].replace("Z", "+00:00")) > cutoff
]

if unanswered:
    for m in unanswered:
        print(f"⚠️ לא ענינו ל-{m['sender_name']}: {m['body'][:80]}")
```

### Cleanup (Weekly)

```python
import json
from datetime import datetime, timedelta, timezone

INBOX = "/opt/ocana/openclaw/workspace/inbox/pending.json"

with open(INBOX) as f:
    data = json.load(f)

cutoff = datetime.now(timezone.utc) - timedelta(days=7)
data["messages"] = [
    m for m in data["messages"]
    if not m["answered"]
    or datetime.fromisoformat(m["ts"].replace("Z", "+00:00")) > cutoff
]

with open(INBOX, "w") as f:
    json.dump(data, f, indent=2)
```

---

## Loop Prevention Rules (CRITICAL)

### Context Isolation
**NEVER** share information across chat contexts:
- Internal status updates → send ONLY to owner, NEVER to other contacts
- Task details from owner's DM → never mention to third parties
- When replying to person X → do NOT include context from conversation with person Y
- Progress reports → owner in private DM only

### Echo Prevention
Before responding to ANY message, check `sender_id` from inbound metadata.
- If sender is your own agent/number → **NO_REPLY** immediately.

### No Duplicate Sends
Before sending to a group or DM:
- Check if identical message was already sent in this session
- If yes → skip.

### Multi-PA Coordination
- Only ONE PA should respond to each group message
- If another PA already responded → stay silent (NO_REPLY)
- Never impersonate another PA without disclosure
- Give other PAs time before intervening

---

## Integration

- **Before each response** → load context via `wa_context`
- **After important exchanges** → log to context.md / notes.md
- **With git-backup** → push after memory updates
- **With owner-briefing** → include DM follow-ups in morning briefing
- **Heartbeat** → check inbox for unanswered messages every 2h

---

## Cost Tips

- All memory operations are file reads/writes — no LLM tokens
- Use `tail -10` instead of reading full context files
- Batch log multiple events before pushing backup
- Small model OK for all memory operations
