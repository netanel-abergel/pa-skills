---
name: ai-pa
description: "AI Personal Assistant network skill for multi-agent PA coordination. Use when: contacting another PA, coordinating with peer agents, scheduling meetings between owners, broadcasting messages to PA groups, or looking up contacts from the local PA directory. Reads contact data from data/pa-directory.json in the workspace."
---

# AI-PA Network Skill

## Minimum Model
Any model that can follow numbered steps and run bash commands.

---

## Directory Setup

All contact and PA data lives in **`contact-list.md`** (workspace root). This is the single source of truth.
For lookups (phone, PA, group JID) → use the **contact-list** skill first, then return here for coordination.

❌ `data/pa-directory.json` is deprecated. Use `contact-list.md` instead.

---

## Group Leadership Rules

Some groups in the PA network have a **designated lead PA**. When a group has a lead:
- **Only the lead PA responds** to questions in that group
- Other PAs stay silent unless explicitly tagged by the lead
- This prevents duplicate/echo answers

### Current Group Ownership

| Group | JID | Lead PA | Rule |
|---|---|---|---|
| PA Onboarding | 120363408613668489@g.us | Heleni | Heleni responds to all questions. All other PAs: **stay silent** unless Heleni tags you. |

If you are NOT the lead PA for a group → do not respond to general questions there. You may still respond if:
1. Heleni (the lead) directly tags your name
2. Your owner sends a message directly to you in the group

---

## Core Rules

**Contact the PA (not the owner) for:**
- Scheduling meetings
- Passing messages between owners
- Coordination and follow-ups

**Contact the owner directly only when:**
- Their PA is unresponsive for >1 hour on a time-sensitive matter
- Explicitly instructed by your owner

**Never contact an owner directly** if `contact_preference` is `"pa_only"`.

---

## Task Templates

### Find a PA's Contact

Use the **contact-list** skill → lookup by owner name in `contact-list.md`.
The PA column shows `PA_NAME (+phone)`. The Active PAs section has full details.

```bash
grep -i "OWNER_NAME" /opt/ocana/openclaw/workspace/contact-list.md
```

If no match found → ask your owner for the contact details.

### Schedule a Meeting

```
1. Find the other PA's phone from pa-directory.json (use script above)
2. Message the PA:
   "Hey [PA Name], [your owner] wants to meet [their owner].
    Are they available [proposed time]? Or what works best?"
3. Wait for reply. If no reply after 2 hours on a business day:
   → Follow up once.
   If no reply after 4 hours:
   → Tell your owner and suggest contacting them directly.
4. Once agreed, create calendar event:
   GOG_ACCOUNT=owner@company.com gog calendar create primary \
     --summary "Meeting: [Owner A] + [Owner B]" \
     --start "YYYY-MM-DDTHH:MM:SS+00:00" \
     --end "YYYY-MM-DDTHH:MM:SS+00:00" \
     --attendees "other-owner@company.com"
5. Confirm with both PAs
```

### Broadcast to All PAs

```
1. Find the group JID with purpose "pa_coordination" in pa-directory.json
2. Send to the group (not individual DMs)
3. For personal follow-ups only: DM each PA individually
```

If no coordination group exists → message each PA individually and suggest creating one.

### Send Email on Owner's Behalf

**Always confirm with owner before sending.**

```bash
GOG_ACCOUNT=owner@company.com gog gmail send \
  --to "recipient@company.com" \
  --subject "Subject" \
  --body "Body"
```

If `gog` returns an auth error:
```bash
gog auth add owner@company.com --services gmail
# Then retry the send command
```

---

## Add a New PA to Directory

Use the **contact-list** skill's "Add a New PA" flow. It updates `contact-list.md` with:
1. New row in Active PAs table
2. PA info in the owner's contact row
3. New DM target in PA Sync List
4. Git push

---

## PA Unresponsive Protocol

1. Try messaging their phone number again
2. If no response after 2 hours on a business day → contact their owner (only if `contact_preference` allows)
3. Log the issue in your memory files

---

## Quick Reference

| Task | Action |
|---|---|
| Find PA phone | Use contact-list skill → grep contact-list.md |
| Schedule meeting | Contact other PA → agree time → create calendar event |
| Broadcast message | Use PA coordination group JID |
| Billing issue | See billing-monitor skill |
| New PA | Use contact-list skill → add to contact-list.md → announce in group |
| PA unresponsive | Wait 2h → contact owner if urgent |
| Directory missing | Create from schema above |

---

## Cost Tips

- **Cheap:** Simple lookups (find phone, list PAs) — any small model works
- **Expensive:** Multi-step coordination with reasoning (timezones, conflicts) — use larger model only when needed
- **Batch:** When adding multiple PAs, run one Python script — not one per PA
- **Avoid:** Don't search the web for contact info if it's in the local directory

---

## Error Reference

| Error | Cause | Fix |
|---|---|---|
| `pa-directory.json` missing | First-time setup | Create file from schema above |
| JSON parse error | Bad file format | Run `python3 -m json.tool data/pa-directory.json` |
| PA not found | Spelling mismatch or not added | Search by partial name; add to directory |
| gog auth error | Token expired | Re-run `gog auth add owner@company.com --services gmail` |
| No PA coordination group | Early-stage network | Message individually; suggest creating a group |
