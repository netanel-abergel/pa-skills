---
name: owner-briefing
description: "Generate and send a daily briefing to your owner covering today's meetings, urgent emails, open tasks, and anything that needs attention. Use when: it's the start of the owner's day, when asked for a summary, or on a scheduled cron job."
---

# Owner Briefing Skill

Prepare and deliver a daily briefing to your owner every morning.

---

## Briefing Format

```
☀️ Good morning [Owner Name] — here's your day:

📅 TODAY'S MEETINGS
• 09:30 — Standup with team (30 min)
• 14:00 — 1:1 with [Person] (1h)
• 16:00 — Product review (45 min)

📬 EMAILS NEEDING ATTENTION
• [Sender] — "[Subject]" (received 2h ago)
• [Sender] — "[Subject]" (flagged urgent)

✅ OPEN TASKS
• Follow up with [Person] re: [topic]
• Review PR from [Name]
• [Any other pending items]

⚠️ HEADS UP
• [Anything unusual, deadline approaching, etc.]

Have a great day! 🙌
```

---

## Building the Briefing

### 1. Get Today's Calendar Events

```bash
#!/bin/bash
set -e

TODAY=$(date -u +%Y-%m-%dT00:00:00Z)
# Cross-platform tomorrow: Linux uses -d, macOS uses -v
TOMORROW=$(date -u -d '+1 day' +%Y-%m-%dT00:00:00Z 2>/dev/null || date -u -v+1d +%Y-%m-%dT00:00:00Z)

GOG_ACCOUNT=owner@company.com gog calendar events primary \
  --from "$TODAY" \
  --to "$TOMORROW" \
  2>/dev/null \
  | python3 -c "
import sys, json
try:
    raw = sys.stdin.read().strip()
    events = json.loads(raw) if raw else []
except json.JSONDecodeError:
    events = []
print('📅 TODAY\'S MEETINGS')
if not events:
    print('• No events found')
else:
    for e in sorted(events, key=lambda x: x.get('start', {}).get('dateTime', '')):
        start = e.get('start', {}).get('dateTime', '')[:16].replace('T', ' ')
        summary = e.get('summary', 'Untitled')
        print(f'• {start} — {summary}')
"
```

### 2. Get Urgent Emails

```bash
#!/bin/bash
set -e

GOG_ACCOUNT=owner@company.com gog gmail search \
  'is:unread newer_than:1d' \
  --max 5 \
  2>/dev/null \
  | python3 -c "
import sys, json
try:
    raw = sys.stdin.read().strip()
    emails = json.loads(raw) if raw else []
except json.JSONDecodeError:
    emails = []
print('📬 EMAILS NEEDING ATTENTION')
if not emails:
    print('• No urgent emails')
else:
    for e in emails:
        sender = e.get('from', 'Unknown')
        subject = e.get('subject', '(no subject)')
        print(f'• {sender} — \"{subject}\"')
"
```

### 3. Pull Open Tasks (monday.com)

```bash
#!/bin/bash
set -e

MONDAY_TOKEN_FILE="$HOME/.credentials/monday-api-token.txt"
if [ ! -f "$MONDAY_TOKEN_FILE" ]; then
  echo "✅ OPEN TASKS"
  echo "• (monday.com token not configured)"
  exit 0
fi

MONDAY_TOKEN=$(cat "$MONDAY_TOKEN_FILE")
BOARD_ID="BOARD_ID"  # replace with actual board ID

RESPONSE=$(curl -s -X POST https://api.monday.com/v2 \
  -H "Content-Type: application/json" \
  -H "Authorization: $MONDAY_TOKEN" \
  -d "{\"query\": \"{ boards(ids: [$BOARD_ID]) { items_page(limit: 5) { items { name state } } } }\"}")

echo "$RESPONSE" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    items = d['data']['boards'][0]['items_page']['items']
except (KeyError, IndexError, json.JSONDecodeError) as e:
    print('✅ OPEN TASKS')
    print(f'• (could not fetch: {e})')
    sys.exit(0)
print('✅ OPEN TASKS')
open_items = [i for i in items if i.get('state') != 'done']
if not open_items:
    print('• None — all clear!')
else:
    for item in open_items:
        print(f'• {item[\"name\"]}')
"
```

---

## Sending the Briefing

```bash
# Via WhatsApp
openclaw message send --to OWNER_PHONE --message "$BRIEFING"

# Via Email
GOG_ACCOUNT=owner@company.com gog gmail send \
  --to owner@company.com \
  --subject "☀️ Your Daily Briefing — $(date +%A\ %B\ %d)" \
  --body "$BRIEFING"
```

---

## Scheduling via Cron

Add to OpenClaw cron config:

```json
{
  "jobs": [
    {
      "id": "morning-briefing",
      "schedule": "30 7 * * 1-5",
      "timezone": "Asia/Jerusalem",
      "task": "Run owner briefing and send to owner",
      "delivery": {
        "mode": "message",
        "channel": "whatsapp",
        "to": "OWNER_PHONE"
      }
    }
  ]
}
```

- Runs Monday–Friday at 07:30 in owner's timezone
- Change `"30 7"` for a different time
- Change timezone to match your owner's location

---

## Customization

Edit the briefing to your owner's preferences:

| Preference | Config |
|---|---|
| Only show meetings after 9am | Filter events by start time |
| Skip internal standups | Exclude events with keyword "standup" |
| Include weather | Add weather check before sending |
| Include news digest | Pull top headlines from RSS |
| Highlight flagged emails only | Filter by `is:starred` or `is:important` |

---

## Evening Briefing (Optional)

A lighter version for end of day — what's tomorrow:

```
🌙 Tomorrow's preview for [Owner]:

📅 TOMORROW
• [Events list]

📋 PREP NEEDED
• [Anything to prepare overnight]
```

Send at 18:00 on working days.

---

## Model Compatibility

This skill works with any LLM model. The briefing generation requires only basic summarization and formatting.

| Task | Minimum Model |
|---|---|
| Fetching calendar/email data | Any (CLI-based, no LLM needed) |
| Formatting and sending briefing | Any small/lightweight model |
| Identifying "urgent" signals | Small–Medium model |
| Adding personalized commentary | Medium model recommended |

No provider-specific APIs or features are used. The gog CLI handles all Google Workspace access.
