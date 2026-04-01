---
name: group-memory
description: "Maintain separate memory contexts per WhatsApp group. Use when: the agent participates in multiple WhatsApp groups and needs to track topics, decisions, people, and context per group separately. Prevents context bleed between groups and enables targeted recall per group."
---

# Group Memory Skill

Separate, searchable memory per WhatsApp group — prevents mixing context between family, work, and PA groups.

---

## The Problem

Without group memory:
- Context from one group bleeds into another
- Agent doesn't know what was discussed in group X vs group Y
- Hard to recall "what did we decide in the leadership group last week?"

With group memory:
- Each group has its own context file
- Separate people, topics, decisions per group
- Targeted recall: "what was discussed in PA Onboarding this week?"

---

## Directory Structure

```
memory/
  groups/
    120363408613668489/        ← JID (sanitized)
      meta.json                ← Group name, JID, participants
      context.md               ← Running context for this group
      decisions.md             ← Key decisions made in this group
      people.md                ← Who participates and their role/tone
    120363422865795623/
      meta.json
      context.md
      ...
    direct-+1XXXXXXXXXX/       ← DM with specific person
      context.md
      ...
```

---

## Setup

### Initialize group memory directory

```bash
mkdir -p ~/.openclaw/workspace/memory/groups

# Create a group entry
init_group() {
  JID="$1"
  NAME="$2"
  SAFE_JID=$(echo "$JID" | tr '@.' '-')
  DIR="$HOME/.openclaw/workspace/memory/groups/$SAFE_JID"
  
  mkdir -p "$DIR"
  
  cat > "$DIR/meta.json" << EOF
{
  "jid": "$JID",
  "name": "$NAME",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "type": "group"
}
EOF

  touch "$DIR/context.md"
  touch "$DIR/decisions.md"
  touch "$DIR/people.md"
  
  echo "Initialized group memory: $NAME ($JID)"
}

# Example:
# init_group "120363408613668489@g.us" "PA Onboarding"
```

---

## Writing to Group Memory

### Log a message or event

```bash
log_to_group() {
  JID="$1"
  CONTENT="$2"
  SAFE_JID=$(echo "$JID" | tr '@.' '-')
  FILE="$HOME/.openclaw/workspace/memory/groups/$SAFE_JID/context.md"
  
  TIMESTAMP=$(date -u +%Y-%m-%d\ %H:%M)
  echo "[$TIMESTAMP] $CONTENT" >> "$FILE"
}

# Usage:
# log_to_group "120363408613668489@g.us" "Kira reported calendar connected successfully"
```

### Log a decision

```bash
log_decision() {
  JID="$1"
  DECISION="$2"
  SAFE_JID=$(echo "$JID" | tr '@.' '-')
  FILE="$HOME/.openclaw/workspace/memory/groups/$SAFE_JID/decisions.md"
  
  DATE=$(date -u +%Y-%m-%d)
  echo "## [$DATE] $DECISION" >> "$FILE"
}
```

### Log a person (when you learn something about a participant)

```bash
log_person() {
  JID="$1"
  PERSON_NAME="$2"
  NOTE="$3"
  SAFE_JID=$(echo "$JID" | tr '@.' '-')
  FILE="$HOME/.openclaw/workspace/memory/groups/$SAFE_JID/people.md"
  
  echo "- **$PERSON_NAME**: $NOTE" >> "$FILE"
}
```

---

## Reading Group Memory

### Get full context for a group

```bash
get_group_context() {
  JID="$1"
  SAFE_JID=$(echo "$JID" | tr '@.' '-')
  DIR="$HOME/.openclaw/workspace/memory/groups/$SAFE_JID"
  
  if [ ! -d "$DIR" ]; then
    echo "No memory for this group yet."
    return
  fi
  
  echo "=== $(cat $DIR/meta.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('name','Unknown'))") ==="
  echo ""
  echo "--- Recent Context ---"
  tail -20 "$DIR/context.md" 2>/dev/null || echo "(empty)"
  echo ""
  echo "--- Decisions ---"
  cat "$DIR/decisions.md" 2>/dev/null || echo "(none)"
  echo ""
  echo "--- People ---"
  cat "$DIR/people.md" 2>/dev/null || echo "(none)"
}
```

### Search across all groups

```bash
search_groups() {
  QUERY="$1"
  GROUPS_DIR="$HOME/.openclaw/workspace/memory/groups"
  
  echo "Searching for: '$QUERY'"
  grep -r "$QUERY" "$GROUPS_DIR" --include="*.md" -l 2>/dev/null | while read file; do
    GROUP_DIR=$(dirname "$file")
    NAME=$(cat "$GROUP_DIR/meta.json" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('name','?'))" 2>/dev/null)
    echo "Found in: $NAME"
    grep -n "$QUERY" "$file"
    echo ""
  done
}
```

---

## Usage in Conversations

When a message arrives from a group, inject relevant context:

```
On every group message:
1. Extract JID from inbound metadata
2. Load last 10 lines of memory/groups/{JID}/context.md
3. Inject into context before responding:
   "Context for this group: [content]"
4. After responding: log relevant new info to group memory
```

### What to log automatically

| Event | Log to |
|---|---|
| Decision made | decisions.md |
| Task assigned | context.md |
| New participant introduced | people.md |
| Problem reported | context.md |
| Resolution reached | decisions.md |
| Important question asked | context.md |

### What NOT to log
- Casual chitchat
- Repeated/duplicate information
- Greetings and reactions

---

## Group Registry

Maintain a central registry for quick lookup:

```bash
# ~/.openclaw/workspace/data/groups.json
{
  "groups": [
    {
      "name": "PA Onboarding",
      "jid": "XXXXXXXXXXX@g.us",
      "purpose": "Onboarding new PA agents",
      "memory_path": "memory/groups/XXXXXXXXXXX-g-us/"
    },
    {
      "name": "PA Team",
      "jid": "XXXXXXXXXXX@g.us",
      "purpose": "PA coordination and updates",
      "memory_path": "memory/groups/XXXXXXXXXXX-g-us/"
    }
  ]
}
```

---

## Weekly Digest Per Group

Generate a summary of what happened in each group this week:

```bash
weekly_group_digest() {
  GROUPS_DIR="$HOME/.openclaw/workspace/memory/groups"
  WEEK_AGO=$(date -u -d '7 days ago' +%Y-%m-%d 2>/dev/null || date -u -v-7d +%Y-%m-%d)
  
  for group_dir in "$GROUPS_DIR"/*/; do
    NAME=$(cat "$group_dir/meta.json" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('name','?'))" 2>/dev/null)
    RECENT=$(grep "^\\[$WEEK_AGO\\|^\\[202" "$group_dir/context.md" 2>/dev/null | tail -10)
    
    if [ -n "$RECENT" ]; then
      echo "### $NAME"
      echo "$RECENT"
      echo ""
    fi
  done
}
```

---

## Integration with ai-pa Skill

When using ai-pa to coordinate across groups:
1. Load group memory for the relevant group before acting
2. After coordination: log the outcome to both groups' memory

```bash
# Before sending a coordination message to a group:
get_group_context "$TARGET_GROUP_JID"

# After successful coordination:
log_to_group "$TARGET_GROUP_JID" "Coordination with [other group]: [outcome]"
```

---

## Model Notes

- Any model can manage group memory files
- For summarization of long context files: medium+ model recommended
- For search and retrieval: any model works
