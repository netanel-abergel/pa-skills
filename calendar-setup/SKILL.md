---
name: calendar-setup
description: "Step-by-step wizard for connecting an owner's Google Calendar to their OpenClaw PA agent, including granting write permissions. Use when: setting up calendar access for the first time, troubleshooting calendar connection issues, fixing read-only calendar access, or re-authenticating after permission errors."
---

# Calendar Setup Skill

Connect an owner's Google Calendar to their OpenClaw PA with full read/write access.

---

## Overview

Two accounts are involved:
- **Agent email** — the PA's own Google account (e.g. `aria@openclaw.ai`)
- **Owner email** — the human's Google account (e.g. `jane@company.com`)

The agent must be granted access to the **owner's** calendar — they are separate accounts.

---

## Step 1 — Owner Shares Calendar

The **owner** must do this in Google Calendar:

1. Open [calendar.google.com](https://calendar.google.com)
2. Click the three dots next to their primary calendar → **Settings and sharing**
3. Under **Share with specific people** → click **+ Add people**
4. Enter the **agent email** (e.g. `aria@openclaw.ai`)
5. Set permission to **"Make changes to events"** (not just "See all event details")
6. Click **Send**

✅ Owner's calendar is now shared with write access.

---

## Step 2 — Agent Authenticates

The **PA agent** runs:

```bash
# Add the owner's account to gog
gog auth add owner@company.com --services gmail,calendar,drive,contacts

# Verify auth list
gog auth list
```

If re-authenticating:
```bash
gog auth remove owner@company.com
gog auth add owner@company.com --services gmail,calendar,drive,contacts
```

---

## Step 3 — Test Write Access

```bash
# Test: create a test event (delete after)
GOG_ACCOUNT=owner@company.com gog calendar create primary \
  --summary "PA Setup Test — delete me" \
  --start "$(date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%SZ)" \
  --end "$(date -u -d '+2 hours' +%Y-%m-%dT%H:%M:%SZ)"
```

Expected: Event appears in owner's Google Calendar.

---

## Common Issues

### "Connected" in dashboard but agent can't write

**Cause:** The OpenClaw dashboard shows the agent's own calendar connection, not the owner's calendar.

**Fix:**
1. Confirm owner shared their calendar with the agent email (Step 1)
2. Confirm agent added the owner's account to gog (Step 2)
3. When creating events, always specify: `GOG_ACCOUNT=owner@company.com`

### "Insufficient permissions" error

**Cause:** Calendar was shared with "See all event details" instead of "Make changes to events".

**Fix:** Owner repeats Step 1 and changes permission level.

### "Token expired" / auth failure

**Fix:**
```bash
gog auth remove owner@company.com
gog auth add owner@company.com --services calendar
```

### Multiple calendars (work + personal)

If the owner has separate work and personal calendars:
```bash
# List available calendars
GOG_ACCOUNT=owner@company.com gog calendar list

# Use specific calendar ID instead of "primary"
GOG_ACCOUNT=owner@company.com gog calendar create CALENDAR_ID \
  --summary "Meeting" ...
```

---

## Verification Checklist

- [ ] Owner has shared calendar with agent email
- [ ] Permission level is "Make changes to events"
- [ ] Agent has added owner's account via `gog auth add`
- [ ] Test event created successfully
- [ ] Test event deleted after verification
- [ ] Agent uses `GOG_ACCOUNT=owner@company.com` for all calendar operations

---

## Useful Commands

```bash
# List all authenticated accounts
gog auth list

# List calendar events (next 7 days)
GOG_ACCOUNT=owner@company.com gog calendar events primary \
  --from $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --to $(date -u -d '+7 days' +%Y-%m-%dT%H:%M:%SZ)

# Create event with attendees
GOG_ACCOUNT=owner@company.com gog calendar create primary \
  --summary "Meeting title" \
  --start "2026-04-02T10:00:00+03:00" \
  --end "2026-04-02T11:00:00+03:00" \
  --attendees "attendee@company.com"

# Delete event
GOG_ACCOUNT=owner@company.com gog calendar delete primary EVENT_ID
```
