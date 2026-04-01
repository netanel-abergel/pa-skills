---
name: meeting-scheduler
description: "Schedule meetings between your owner and another person by coordinating with their PA, finding available slots in both calendars, and sending a calendar invite. Use when: your owner wants to meet with someone, needs to find a common free slot, or asks you to set up a meeting."
---

# Meeting Scheduler Skill

Coordinate and book meetings between your owner and another party.

---

## Full Scheduling Flow

### Step 1 — Get the Request

Understand:
- Who does your owner want to meet?
- Approximate duration (default: 30 min)
- Preferred timeframe (this week, next week, mornings only, etc.)
- Meeting type (in-person, video call, phone)

### Step 2 — Find the Other Party's PA

Check `data/pa-directory.json`:
```bash
python3 -c "
import json
with open('data/pa-directory.json') as f:
    d = json.load(f)
name = 'Person Name'  # replace
for p in d['pas']:
    if name.lower() in p['owner'].lower():
        print(f\"PA: {p['name']} | Phone: {p['phone']}\")
"
```

### Step 3 — Check Your Owner's Availability

```bash
# Get free/busy for next 5 days
GOG_ACCOUNT=owner@company.com gog calendar events primary \
  --from $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --to $(date -u -d '+5 days' +%Y-%m-%dT%H:%M:%SZ) \
  | python3 -c "
import sys, json
events = json.load(sys.stdin)
for e in events:
    print(f\"{e.get('start',{}).get('dateTime','')} — {e.get('summary','')}\")
"
```

### Step 4 — Contact the Other PA

```
Message to [Other PA]:
"Hey [PA Name], [Your Owner] would like to schedule a [30-min] meeting 
with [Their Owner] — ideally [this week / next week].

Here are some slots that work for [Your Owner]:
• [Date] [Time] – [Time]
• [Date] [Time] – [Time]
• [Date] [Time] – [Time]

Do any of these work? Or what times work best?"
```

### Step 5 — Confirm and Book

Once both sides agree on a time:

```bash
# Create the event
GOG_ACCOUNT=owner@company.com gog calendar create primary \
  --summary "Meeting: [Owner A] + [Owner B]" \
  --start "YYYY-MM-DDTHH:MM:SS+TZ" \
  --end "YYYY-MM-DDTHH:MM:SS+TZ" \
  --attendees "other-owner@company.com" \
  --description "Scheduled via PA coordination"
```

### Step 6 — Confirm Both Sides

```
To your owner:
"✅ Meeting booked: [Date] [Time] with [Other Person]. Calendar invite sent."

To the other PA:
"✅ Invite sent to [Their Owner] for [Date] [Time]. Let me know if anything changes."
```

---

## Finding Available Slots (Script)

```bash
python3 << 'EOF'
import subprocess, json
from datetime import datetime, timedelta, timezone

# Get events for next 7 days
result = subprocess.run(
    ['gog', 'calendar', 'events', 'primary',
     '--from', datetime.now(timezone.utc).isoformat(),
     '--to', (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()],
    env={'GOG_ACCOUNT': 'owner@company.com', 'PATH': '/usr/bin:/bin'},
    capture_output=True, text=True
)

events = json.loads(result.stdout) if result.stdout else []
busy_times = [(e['start']['dateTime'], e['end']['dateTime']) for e in events if 'dateTime' in e.get('start', {})]

# Suggest free slots (working hours: 09:00–18:00)
suggestions = []
for day_offset in range(1, 8):
    day = datetime.now(timezone.utc) + timedelta(days=day_offset)
    if day.weekday() >= 5:  # Skip weekends
        continue
    for hour in [9, 11, 14, 16]:
        slot_start = day.replace(hour=hour, minute=0, second=0, microsecond=0)
        slot_end = slot_start + timedelta(minutes=30)
        # Check if slot is free
        conflict = any(
            slot_start.isoformat() < e[1] and slot_end.isoformat() > e[0]
            for e in busy_times
        )
        if not conflict:
            suggestions.append(f"{slot_start.strftime('%A %b %d')} at {slot_start.strftime('%H:%M')}")
        if len(suggestions) >= 5:
            break
    if len(suggestions) >= 5:
        break

print("Available slots:")
for s in suggestions:
    print(f"  • {s}")
EOF
```

---

## Rescheduling

If a meeting needs to change:

1. Get the event ID: `GOG_ACCOUNT=owner@company.com gog calendar events primary`
2. Delete old event: `GOG_ACCOUNT=owner@company.com gog calendar delete primary EVENT_ID`
3. Coordinate new time with other PA
4. Create new event

---

## Quick Templates

**Request availability:**
> "Hey [PA], [Owner A] wants to connect with [Owner B] for ~[30 min] this week. What works?"

**Propose slots:**
> "Here are 3 options: [A], [B], [C]. Any of these work?"

**Confirm booking:**
> "✅ Booked for [time]. Invite sent."

**Decline/reschedule:**
> "[Owner] can't make [time]. Can we try [alternative]?"
