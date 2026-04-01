---
name: pa-status
description: "PA network health dashboard. Use when: checking if all PAs in the network are active, checking billing status, verifying calendar connections, or generating a network status report. Reads from data/pa-directory.json."
---

# PA Status Skill

Monitor the health of all PAs in your network.

---

## Status Checks

For each PA in `data/pa-directory.json`, check:

| Check | How | Healthy |
|---|---|---|
| Reachability | Send a ping message | Response within 5 min |
| Last active | Check last message timestamp | Within 24h |
| Billing | Check for billing error logs | No errors in last 24h |
| Model | Confirm current model | Matches expected |
| Calendar | Confirm calendar is connected | Connected + write access |

---

## Running a Status Check

### Quick Ping (WhatsApp)

```
For each PA in directory:
  Send: "ping 🏓"
  Wait up to 5 minutes for response
  Log: ONLINE / NO_RESPONSE
```

### Status Report Format

```
📊 PA Network Status — [DATE]

✅ ONLINE (X/Y)
• Aria (Jane's PA) — last seen 2h ago, Claude Sonnet 4.6, calendar ✅
• Rex (John's PA) — last seen 30m ago, GPT-4o, calendar ✅

⚠️ ISSUES
• Nova (Sarah's PA) — billing error since 14:00
• Bolt (Mike's PA) — no response in 6h

❌ OFFLINE
• (none)

Action needed: Nova billing, Bolt unresponsive
```

---

## Automated Report

Generate and send to admin:

```bash
python3 << 'EOF'
import json, datetime

with open('data/pa-directory.json') as f:
    d = json.load(f)

report = f"📊 PA Network Status — {datetime.date.today()}\n\n"

for pa in d['pas']:
    status = pa.get('status', 'unknown')
    name = pa['name']
    owner = pa['owner']
    model = pa.get('model', 'unknown')
    calendar = "✅" if pa.get('calendar_connected') else "❌"
    billing = "✅" if not pa.get('billing_error') else "⚠️ billing"
    report += f"• {name} ({owner}) — {model}, calendar {calendar}, billing {billing}\n"

print(report)
EOF
```

---

## Directory Schema Extension

Add these fields to each PA entry in `pa-directory.json` to track status:

```json
{
  "name": "Aria",
  "model": "claude-sonnet-4-6",
  "last_seen": "2026-04-01T10:00:00Z",
  "calendar_connected": true,
  "billing_error": false,
  "billing_error_since": null,
  "status": "active"
}
```

---

## Scheduling

Run status checks:
- **Daily at 09:00** — full network report to admin
- **On billing error detection** — immediate partial report
- **On demand** — when admin asks "what's the status?"
