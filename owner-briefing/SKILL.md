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
TODAY=$(date -u +%Y-%m-%dT00:00:00Z)
TOMORROW=$(date -u -d '+1 day' +%Y-%m-%dT00:00:00Z)

GOG_ACCOUNT=owner@company.com gog calendar events primary \
  --from "$TODAY" \
  --to "$TOMORROW" \
  | python3 -c "
import sys, json
events = json.load(sys.stdin)
print('📅 TODAY\'S MEETINGS')
for e in sorted(events, key=lambda x: x.get('start', {}).get('dateTime', '')):
    start = e.get('start', {}).get('dateTime', '')[:16].replace('T', ' ')
    summary = e.get('summary', 'Untitled')
    print(f'• {start} — {summary}')
"
```

### 2. Get Urgent Emails

```bash
GOG_ACCOUNT=owner@company.com gog gmail search \
  'is:unread newer_than:1d' \
  --max 5 \
  | python3 -c "
import sys, json
emails = json.load(sys.stdin)
print('📬 EMAILS NEEDING ATTENTION')
for e in emails:
    sender = e.get('from', 'Unknown')
    subject = e.get('subject', '(no subject)')
    print(f'• {sender} — \"{subject}\"')
"
```

### 3. Pull Open Tasks (monday.com)

```bash
MONDAY_TOKEN=$(cat ~/.credentials/monday-api-token.txt)
curl -s -X POST https://api.monday.com/v2 \
  -H "Content-Type: application/json" \
  -H "Authorization: $MONDAY_TOKEN" \
  -d "{\"query\": \"{ boards(ids: [BOARD_ID]) { items_page(limit: 5) { items { name state } } } }\" }" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
items = d['data']['boards'][0]['items_page']['items']
print('✅ OPEN TASKS')
for item in items:
    if item['state'] != 'done':
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
