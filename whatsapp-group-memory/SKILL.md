---
name: whatsapp-group-memory
description: "Maintain separate memory contexts per WhatsApp conversation — both groups and direct messages (DMs). Use when: tracking what was discussed with a specific person or in a specific group, recalling past context before responding, logging decisions or key facts from a conversation, or preventing context bleed between different chats."
---

# WhatsApp Memory Skill

Separate, searchable memory per WhatsApp conversation — groups AND direct messages.

---

## Why This Matters

Without conversation memory:
- Context from one chat bleeds into another
- Hard to recall "what did Guy say last week?"
- Can't track decisions made in a specific group
- Owner repeats themselves across sessions

With WhatsApp memory:
- Every group and DM has its own context file
- Recall: "what was discussed in the PA Team group this month?"
- Track: "what did Doron ask me to follow up on?"
- Separate memory for family, work, PA network

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
        people.md                 ← who participates and their style/role
    dms/
      972548834688/               ← sanitized phone number
        meta.json                 ← name, phone, relationship
        context.md                ← running DM context
        notes.md                  ← tasks, preferences, important facts
```

---

## Setup

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
# init_whatsapp_memory "group" "120363422865795623@g.us" "Monday PA Team"
# init_whatsapp_memory "dm" "+972542010180" "Guy Atzmon"
```

---

## Writing Memory

### Log to a conversation

```bash
wa_log() {
  TYPE="$1"    # group or dm
  ID="$2"      # JID or phone
  CONTENT="$3"
  FILE_NAME="${4:-context.md}"  # context.md / decisions.md / notes.md
  
  SAFE_ID=$(echo "$ID" | tr '@.+' '---')
  BASE="$HOME/.openclaw/workspace/memory/whatsapp"
  
  if [ "$TYPE" = "group" ]; then
    FILE="$BASE/groups/$SAFE_ID/$FILE_NAME"
  else
    FILE="$BASE/dms/$SAFE_ID/$FILE_NAME"
  fi
  
  [ ! -f "$FILE" ] && mkdir -p "$(dirname "$FILE")" && touch "$FILE"
  echo "[$(date -u +%Y-%m-%d\ %H:%M)] $CONTENT" >> "$FILE"
}

# Usage:
# wa_log "group" "120363422865795623@g.us" "Kira reported calendar connected ✅"
# wa_log "dm" "+972542010180" "Guy asked to fix Alfred's calendar access" "notes.md"
# wa_log "dm" "+972547691235" "Decided: Midgee will re-auth calendar tomorrow" "notes.md"
```

---

## Reading Memory

### Get context for a conversation

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
  
  [ ! -d "$DIR" ] && echo "No memory for this conversation yet." && return
  
  NAME=$(cat "$DIR/meta.json" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('name','?'))" 2>/dev/null)
  echo "=== $NAME ==="
  echo "--- Recent ---"
  tail -$LINES "$DIR/context.md" 2>/dev/null || echo "(empty)"
  echo "--- Notes/Decisions ---"
  cat "$DIR/notes.md" "$DIR/decisions.md" 2>/dev/null | tail -10 || echo "(none)"
}
```

### Search across all WhatsApp memory

```bash
wa_search() {
  QUERY="$1"
  BASE="$HOME/.openclaw/workspace/memory/whatsapp"
  
  echo "Searching WhatsApp memory for: '$QUERY'"
  grep -r "$QUERY" "$BASE" --include="*.md" -l 2>/dev/null | while read file; do
    DIR=$(dirname "$file")
    NAME=$(cat "$DIR/meta.json" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('name','?'))" 2>/dev/null)
    echo "Found in: $NAME"
    grep -n "$QUERY" "$file" | head -3
    echo ""
  done
}
```

---

## What to Log

### In groups:
| Event | File |
|---|---|
| Decision reached | decisions.md |
| Task assigned to someone | context.md |
| New person introduced | people.md |
| Problem reported | context.md |
| Outcome / resolution | decisions.md |

### In DMs:
| Event | File |
|---|---|
| Task owner gave you | notes.md |
| Preference or rule they stated | notes.md |
| Follow-up promised | notes.md |
| Important fact about this person | notes.md |
| Regular conversation context | context.md |

### Never log:
- Casual greetings, reactions
- Duplicate information already in notes
- Sensitive credentials or secrets

---

## Before Responding (Inject Context)

On every incoming message, load context for that chat:

```
1. Extract JID or phone from inbound metadata
2. Run: wa_context "group"|"dm" "$ID" 10
3. Use context to inform response
4. After responding: log anything worth remembering
```

---

## Weekly Digest

```bash
wa_weekly_digest() {
  BASE="$HOME/.openclaw/workspace/memory/whatsapp"
  WEEK_AGO=$(date -u -d '7 days ago' +%Y-%m-%d 2>/dev/null || date -u -v-7d +%Y-%m-%d)
  
  echo "# WhatsApp Memory Digest — Week of $WEEK_AGO"
  
  for dir in "$BASE"/groups/*/ "$BASE"/dms/*/; do
    [ -d "$dir" ] || continue
    NAME=$(cat "$dir/meta.json" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('name','?'))" 2>/dev/null)
    RECENT=$(grep "$WEEK_AGO\|$(date -u +%Y-%m-%d)" "$dir/context.md" "$dir/notes.md" 2>/dev/null | tail -5)
    [ -n "$RECENT" ] && echo "### $NAME" && echo "$RECENT" && echo ""
  done
}
```

---

## Integration

- **Before each response** → load context for that conversation
- **After important exchanges** → log to context.md or notes.md
- **With git-backup** → push after every memory update
- **With owner-briefing** → include DM follow-ups in morning briefing

---

## Model Notes

- Any model can manage memory files
- Medium+ model recommended for deciding what's worth logging
- No external dependencies — pure file system
