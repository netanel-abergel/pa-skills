---
name: meeting-scheduler
description: "Schedule meetings between your owner and another person by coordinating with their PA, finding available slots in both calendars, and sending a calendar invite. Use when: your owner wants to meet with someone, needs to find a common free slot, or asks you to set up a meeting. Handles both PA-to-PA coordination and direct scheduling. Works with any LLM model."
---

# Meeting Scheduler Skill

Coordinate and book meetings between your owner and another party.

---

## Full Scheduling Flow

### Step 1 — Understand the Request

Before doing anything, clarify:
- **Who** does your owner want to meet?
- **Duration** — default to 30 min if not specified
- **Timeframe** — "this week", "next week", "mornings only", etc.
- **Meeting type** — video call, in-person, phone? (affects calendar event details)
- **Urgency** — does it need to happen today, or can it wait a few days?

If the request is ambiguous (e.g. "set up a call with Jane"), ask one quick clarifying question before proceeding.

---

### Step 2 — Find the Other Party's PA

Check `data/pa-directory.json`:

```bash
python3 << 'EOF'
import json, sys

try:
    with open('data/pa-directory.json') as f:
        d = json.load(f)
except FileNotFoundError:
    print("ERROR: data/pa-directory.json not found")
    sys.exit(1)

name = 'Person Name'  # replace with actual name
matches = [p for p in d.get('pas', []) if name.lower() in p['owner'].lower()]

if not matches:
    print(f"No PA found for owner matching '{name}'. Will need to contact owner directly or find another way.")
else:
    for p in matches:
        print(f"PA: {p['name']} | Phone: {p['phone']} | Owner: {p['owner']}")
EOF
```

**If no PA found:** Schedule directly with the owner (skip to Step 4 — book the slot with their email).

---

### Step 3 — Check Your Owner's Availability

```bash
#!/bin/bash
# Get events for the next 5 working days
GOG_ACCOUNT=owner@company.com gog calendar events primary \
  --from "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --to "$(date -u -d '+7 days' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v+7d +%Y-%m-%dT%H:%M:%SZ)" \
  2>/dev/null | python3 -c "
import sys, json

try:
    events = json.load(sys.stdin)
except json.JSONDecodeError:
    print('No events found or calendar not accessible')
    sys.exit(0)

print('Upcoming events:')
for e in sorted(events, key=lambda x: x.get('start', {}).get('dateTime', '')):
    start = e.get('start', {}).get('dateTime', 'All day')[:16].replace('T', ' ')
    summary = e.get('summary', 'Untitled')
    print(f'  {start} — {summary}')
"
```

---

### Step 4 — Contact the Other PA

Once you have 3–5 candidate slots, message the other PA:

```
Template:
"Hey [PA Name], [Your Owner Name] would like to schedule a [30-min] 
meeting with [Their Owner Name] — ideally [this week / next week].

Here are some slots that work:
• [Day, Date] at [HH:MM] [TZ]
• [Day, Date] at [HH:MM] [TZ]
• [Day, Date] at [HH:MM] [TZ]

Do any of these work? Or what times work for [Their Owner]?"
```

**If no response within 2 hours on a business day:** Follow up once. After 4 hours with no reply, inform your owner and suggest contacting the other person directly.

---

### Step 5 — Confirm and Book

Once both sides agree on a time:

```bash
# Create the calendar event
GOG_ACCOUNT=owner@company.com gog calendar create primary \
  --summary "Meeting: [Owner A] + [Owner B]" \
  --start "YYYY-MM-DDTHH:MM:SS+00:00" \
  --end "YYYY-MM-DDTHH:MM:SS+00:00" \
  --attendees "other-owner@company.com" \
  --description "Scheduled via PA coordination"
```

**For video calls**, add the meeting link to the description:
```bash
  --description "Video call: https://meet.google.com/xxx-xxxx-xxx (or paste Zoom/Teams link)"
```

---

### Step 6 — Confirm Both Sides

```
To your owner:
"✅ Done — [Date] at [Time] with [Person]. Calendar invite sent."

To the other PA:
"✅ Invite sent to [Their Owner] for [Date] [Time]. 
Let me know if anything changes."
```

---

## Finding Available Slots (Script)

```bash
python3 << 'EOF'
import subprocess, json, sys
from datetime import datetime, timedelta, timezone

OWNER_EMAIL = "owner@company.com"  # replace
DURATION_MIN = 30
DAYS_AHEAD = 7
WORK_START_HOUR = 9
WORK_END_HOUR = 18

try:
    result = subprocess.run(
        ['gog', 'calendar', 'events', 'primary',
         '--from', datetime.now(timezone.utc).isoformat(),
         '--to', (datetime.now(timezone.utc) + timedelta(days=DAYS_AHEAD)).isoformat()],
        env={'GOG_ACCOUNT': OWNER_EMAIL, 'PATH': '/usr/bin:/usr/local/bin:/bin'},
        capture_output=True, text=True, timeout=30
    )
    events = json.loads(result.stdout) if result.stdout.strip() else []
except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
    print(f"Could not fetch calendar: {e}")
    sys.exit(1)

busy = []
for e in events:
    start = e.get('start', {}).get('dateTime')
    end = e.get('end', {}).get('dateTime')
    if start and end:
        busy.append((start, end))

suggestions = []
for day_offset in range(1, DAYS_AHEAD + 1):
    day = datetime.now(timezone.utc) + timedelta(days=day_offset)
    if day.weekday() >= 5:  # skip Saturday (5) and Sunday (6)
        continue
    for hour in range(WORK_START_HOUR, WORK_END_HOUR - 1, 1):
        slot_start = day.replace(hour=hour, minute=0, second=0, microsecond=0)
        slot_end = slot_start + timedelta(minutes=DURATION_MIN)
        if slot_end.hour > WORK_END_HOUR:
            continue
        conflict = any(
            slot_start.isoformat() < b[1] and slot_end.isoformat() > b[0]
            for b in busy
        )
        if not conflict:
            suggestions.append(slot_start)
        if len(suggestions) >= 5:
            break
    if len(suggestions) >= 5:
        break

if not suggestions:
    print("No available slots found in the next 7 days during working hours.")
else:
    print(f"Available {DURATION_MIN}-min slots:")
    for s in suggestions:
        print(f"  • {s.strftime('%A %b %d')} at {s.strftime('%H:%M')} UTC")
EOF
```

---

## Rescheduling

If a meeting needs to be changed:

```bash
# 1. List upcoming events to find the event ID
GOG_ACCOUNT=owner@company.com gog calendar events primary \
  --from "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --to "$(date -u -d '+14 days' +%Y-%m-%dT%H:%M:%SZ)"

# 2. Delete old event (using ID from previous output)
GOG_ACCOUNT=owner@company.com gog calendar delete primary EVENT_ID

# 3. Re-coordinate and create new event
```

**Always notify both sides when rescheduling:**
```
"Hey [PA], [Owner A] needs to move the [Date] meeting. 
Can we reschedule to [proposed new time]?"
```

---

## Common Scenarios

### Owner wants to meet someone not in the PA directory

1. Ask your owner for the person's email or their PA's contact
2. Schedule directly with the person by emailing them:
   ```bash
   GOG_ACCOUNT=owner@company.com gog gmail send \
     --to "person@company.com" \
     --subject "Meeting request — [Your Owner Name]" \
     --body "Hi [Name], [Owner] would like to schedule a 30-min call. Are you available [date/time options]?"
   ```

### Timezone mismatch between parties

Always confirm both parties' timezones before proposing slots. Express times in both timezones:
```
• Tuesday April 8 at 10:00 AM IST (07:00 UTC / 03:00 AM EDT)
```

### Owner rejects proposed slots

Re-run the availability script with different time windows. Ask owner for any hard constraints (no meetings before 10am, no Fridays, etc.) and filter accordingly.

### Meeting cancelled after booking

```bash
# Delete the calendar event
GOG_ACCOUNT=owner@company.com gog calendar delete primary EVENT_ID

# Notify both PAs
```

---

## Quick Templates

| Situation | Template |
|---|---|
| Initial request | "Hey [PA], [Owner A] wants to connect with [Owner B] for ~[30 min] [this/next] week. What works?" |
| Propose slots | "Here are 3 options: [A], [B], [C]. Any work?" |
| Confirm booking | "✅ Booked for [time]. Invite sent to [email]." |
| Reschedule | "[Owner] can't make [time]. Can we try [alternative]?" |
| Cancellation | "[Owner] needs to cancel [time]. Apologies for the short notice." |
| No PA found | "Hi [Owner Name], [Your Owner] would like to schedule a meeting with you. Are you available [options]?" |

---

## Model Guidance

- **Finding slots and booking:** straightforward — any LLM handles it well
- **Reasoning across timezones or complex constraints:** a more capable model produces fewer errors
- **Composing PA messages:** any model; keep messages short and direct
