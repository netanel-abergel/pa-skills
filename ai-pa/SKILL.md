---
name: ai-pa
description: "AI Personal Assistant network skill for multi-agent PA coordination. Use when: contacting another PA, coordinating with peer agents, scheduling meetings between owners, broadcasting messages to PA groups, or looking up contacts from the local PA directory. Reads contact data from data/pa-directory.json in the workspace. Does NOT contain hardcoded contact data — each PA maintains their own directory file. Note: inter-PA coordination requests often require complex reasoning; prefer a more capable LLM model for ambiguous or multi-step scenarios."
---

# AI-PA Network Skill

Operational guide for AI Personal Assistants working within a multi-agent PA network.

---

## Directory Setup

This skill reads contact data from a local file. Before using, ensure the file exists:

```
data/pa-directory.json
```

If it doesn't exist, create it using the schema below. Each PA maintains their own copy with their own network's data.

### Directory Schema

```json
{
  "pas": [
    {
      "name": "PA Name",
      "phone": "+1XXXXXXXXXX",
      "owner": "Owner Full Name",
      "owner_phone": "+1XXXXXXXXXX",
      "owner_role": "VP Product",
      "owner_email": "owner@company.com",
      "status": "active",
      "notes": ""
    }
  ],
  "groups": [
    {
      "name": "Group Name",
      "jid": "XXXXXXXXXXX@g.us",
      "purpose": "PA coordination / leadership / family"
    }
  ],
  "owners": [
    {
      "name": "Owner Name",
      "phone": "+1XXXXXXXXXX",
      "role": "VP Engineering",
      "email": "owner@company.com",
      "pa": "PA Name",
      "pa_phone": "+1XXXXXXXXXX",
      "contact_preference": "pa_only"
    }
  ]
}
```

### Loading the Directory

```bash
python3 -c "
import sys, json
try:
    with open('data/pa-directory.json') as f:
        d = json.load(f)
except FileNotFoundError:
    print('ERROR: data/pa-directory.json not found. Create it first.')
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f'ERROR: Invalid JSON in pa-directory.json: {e}')
    sys.exit(1)
for pa in d.get('pas', []):
    print(f\"{pa['name']} → {pa['owner']} ({pa['phone']})\")
"
```

---

## Core Rules

### When to Contact a PA vs Owner

**Always contact the PA** for:
- Scheduling meetings between owners
- Passing messages between leadership
- Coordination tasks, follow-ups

**Contact the owner directly** only when:
- Their PA is unavailable or unresponsive for >1 hour on a time-sensitive matter
- Urgent matter that cannot wait
- Explicitly instructed by your own owner

**Never contact an owner directly** if their `contact_preference` is `"pa_only"`.

---

## Task Templates

### Schedule a Meeting

```
1. Identify the other party's PA from pa-directory.json
2. Message the PA (not the owner):
   "Hey [PA], [your owner] would like to meet with [their owner].
    Are they available [proposed time]? Or what works best?"
3. Confirm time with your owner
4. Create calendar event:
   gog calendar create primary \
     --summary "Meeting: [Owner A] + [Owner B]" \
     --start "YYYY-MM-DDTHH:MM:SS+TZ" \
     --end "YYYY-MM-DDTHH:MM:SS+TZ" \
     --attendees "owner@company.com"
5. Confirm with both PAs
```

### Broadcast to All PAs

```
1. Find group JID with purpose "pa_coordination" in pa-directory.json
2. Send to group — do not DM individually unless personal message is needed
3. For follow-ups, DM each PA individually using their phone number
```

If no coordination group exists yet, message each PA's phone individually and suggest creating one.

### Send Email on Owner's Behalf

```bash
# Always confirm with owner before sending external emails
GOG_ACCOUNT=owner@company.com gog gmail send \
  --to "recipient@company.com" \
  --subject "Subject" \
  --body "Body"
```

**Edge case:** If `gog` returns an auth error, re-run `gog auth add owner@company.com --services gmail` and retry.

### Find a PA's Contact

```bash
python3 -c "
import json, sys
try:
    with open('data/pa-directory.json') as f:
        d = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f'ERROR: {e}')
    sys.exit(1)
name = 'owner name to search'  # replace with actual search term
matches = [p for p in d.get('pas', []) if name.lower() in p['owner'].lower()]
if not matches:
    print(f'No PA found for owner matching: {name}')
else:
    for m in matches:
        print(f\"PA: {m['name']} | Phone: {m['phone']} | Owner: {m['owner']}\")
"
```

---

## Operational Protocols

### Billing Error

When a peer PA or your own agent reports a billing error:
1. Notify your owner immediately
2. Contact the admin/budget owner (whoever manages API keys for your organization)
3. Workaround: switch to a non-paid or lower-cost model temporarily in agent settings
4. Do NOT share API keys between agents
5. Full protocol: see `billing-monitor` skill

### New PA Onboarding

Full flow:
1. Agent signup at the organization's agent platform
2. Set up messaging channel (WhatsApp Business recommended)
3. Connect calendar (requires owner to share their calendar with write permissions)
4. Add to pa-directory.json with all fields
5. Announce in PA coordination group

Full guide: see `pa-onboarding` skill

### PA Is Unresponsive

1. Try messaging their phone number directly
2. If no response within a reasonable window → contact their owner with context
   - Only if their `contact_preference` allows direct contact
3. Note the issue in your memory files

**Escalation triggers:**
- PA unresponsive for >2 hours on a business day
- PA owner not reachable either
- Critical time-sensitive task blocked

---

## Communication Style Between PAs

- Be direct and concise — PAs are agents, not humans; small talk wastes tokens
- State the request clearly: what you need, from whom, by when
- If you're relaying a message from your owner, say so: "My owner [name] asked me to..."
- Confirm receipt when you receive a coordination request
- When a PA says they can't help, ask for the best person to contact instead

---

## Updating the Directory

### Add a New PA

```bash
python3 << 'EOF'
import json, sys, os

path = 'data/pa-directory.json'

if not os.path.exists(path):
    print(f"ERROR: {path} not found")
    sys.exit(1)

with open(path, 'r') as f:
    d = json.load(f)

new_pa = {
    'name': 'New PA Name',
    'phone': '+1XXXXXXXXXX',
    'owner': 'Owner Full Name',
    'owner_phone': '+1XXXXXXXXXX',
    'owner_role': 'Role',
    'owner_email': 'owner@company.com',
    'status': 'active',
    'notes': ''
}

# Check for duplicates
existing_phones = [p['phone'] for p in d.get('pas', [])]
if new_pa['phone'] in existing_phones:
    print(f"WARNING: PA with phone {new_pa['phone']} already exists")
    sys.exit(1)

d.setdefault('pas', []).append(new_pa)

with open(path, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f"Added PA: {new_pa['name']} for owner: {new_pa['owner']}")
EOF
```

### Update a PA's Status

```bash
python3 -c "
import json
with open('data/pa-directory.json') as f:
    d = json.load(f)
for pa in d['pas']:
    if pa['phone'] == '+1XXXXXXXXXX':  # replace with actual phone
        pa['status'] = 'inactive'
        break
with open('data/pa-directory.json', 'w') as f:
    json.dump(d, f, indent=2)
print('Done')
"
```

---

## Quick Reference

| Task | Action |
|---|---|
| Find a PA's phone | Check pa-directory.json → pas → name/owner |
| Schedule a meeting | Contact other PA, agree time, create calendar event |
| Broadcast message | Use PA coordination group JID |
| Billing issue | See billing-monitor skill |
| New PA added | Update pa-directory.json + announce in group |
| Owner prefers no direct contact | Check `contact_preference` field before messaging |
| PA unresponsive | Wait 1h, then contact their owner if urgent |
| Directory file missing | Create from schema above; populate before using |

---

## Model Guidance

- **Simple lookups** (find phone, list PAs): any LLM works fine
- **Multi-step coordination** (schedule across timezones, resolve conflicts): use a more capable model for better reasoning
- **Drafting inter-PA messages**: standard models are sufficient; keep messages brief

---

## Error Scenarios

| Error | Cause | Fix |
|---|---|---|
| `pa-directory.json` missing | First-time setup | Create file from schema above |
| JSON parse error | Manual edit introduced syntax error | Validate with `python3 -m json.tool data/pa-directory.json` |
| PA not found by name | Spelling mismatch or not in directory | Search by partial name; update directory |
| Owner says "don't contact directly" | `contact_preference: pa_only` | Route through their PA only |
| No PA coordination group | Early-stage network | Message individually; suggest creating a group |
