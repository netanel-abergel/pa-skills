---
name: calendar-setup
description: "Step-by-step wizard for connecting an owner's Google Calendar to their OpenClaw PA agent, including granting write permissions. Use when: setting up calendar access for the first time, troubleshooting calendar connection issues, fixing read-only calendar access, re-authenticating after permission errors, or handling multiple calendar accounts (work + personal). Works with any LLM model."
---

# Calendar Setup Skill

Connect an owner's Google Calendar to their OpenClaw PA agent with full read/write access.

---

## Overview

Two accounts are involved:
- **Agent email** — the PA's own Google account (e.g. `aria@agentdomain.com`)
- **Owner email** — the human's Google account (e.g. `jane@company.com`)

The agent must be granted access to the **owner's** calendar. These are separate accounts — one being set up in OpenClaw does **not** automatically grant access to the other.

**Important:** The OpenClaw dashboard "calendar connected" status reflects the *agent's own* calendar, not the owner's. Always verify write access explicitly.

---

## Step 1 — Owner Shares Calendar

The **owner** must do this in Google Calendar:

1. Open [calendar.google.com](https://calendar.google.com) while logged in as the **owner**
2. In the left sidebar, find the primary calendar (usually their name) → click the three dots → **Settings and sharing**
3. Under **Share with specific people or groups** → click **+ Add people and groups**
4. Enter the **agent email** (e.g. `aria@agentdomain.com`)
5. Set permission dropdown to **"Make changes to events"** *(not "See all event details" — that is read-only)*
6. Click **Send**
7. The agent will receive an email notification — no action needed from the agent side for this step

✅ Owner's calendar is now shared with write access.

**Troubleshooting Step 1:**
- If the owner can't find their calendar name in the sidebar, it's hidden. Scroll down to "Other calendars" or check Settings.
- Organizational accounts (Google Workspace) may restrict external sharing. The owner may need to ask their IT admin to enable sharing with external addresses.

---

## Step 2 — Agent Authenticates

The **PA agent** runs:

```bash
# Add the owner's Google account to gog
# This will open a browser for OAuth authorization
gog auth add owner@company.com --services gmail,calendar,drive,contacts

# Verify the account was added
gog auth list
```

**Expected output of `gog auth list`:**
```
owner@company.com  [gmail, calendar, drive, contacts]
```

If re-authenticating (token expired or permissions changed):
```bash
gog auth remove owner@company.com
gog auth add owner@company.com --services gmail,calendar,drive,contacts
```

**Troubleshooting Step 2:**
- If `gog` is not found: check PATH or install via your OpenClaw distribution
- If browser doesn't open: run `gog auth add` with the `--no-browser` flag and follow the manual URL flow
- If OAuth fails with "access blocked": the Google account may have security restrictions; owner should allow access in their Google Account → Security → Third-party apps

---

## Step 3 — Test Write Access

```bash
# Test: create a test event (delete after verifying it appears)
GOG_ACCOUNT=owner@company.com gog calendar create primary \
  --summary "PA Setup Test — delete me" \
  --start "$(date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v+1H +%Y-%m-%dT%H:%M:%SZ)" \
  --end "$(date -u -d '+2 hours' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v+2H +%Y-%m-%dT%H:%M:%SZ)"
```

**Expected result:** A test event appears in the owner's Google Calendar in ~30 seconds.

After verifying, delete the test event:
```bash
# Get event ID from previous create output, then:
GOG_ACCOUNT=owner@company.com gog calendar delete primary EVENT_ID
```

---

## Common Issues & Fixes

### "Connected" in dashboard but agent can't write

**Cause:** The OpenClaw dashboard shows the agent's *own* calendar connection, not the owner's calendar.

**Fix:**
1. Confirm owner shared their calendar with the agent email (Step 1) — check Google Calendar → Settings → Share with specific people
2. Confirm agent added the owner's account to gog (Step 2)
3. Always specify `GOG_ACCOUNT=owner@company.com` in commands — never omit this

---

### "Insufficient permissions" error

**Cause:** Calendar was shared with "See all event details" (read-only) instead of "Make changes to events".

**Fix:** Owner repeats Step 1 and changes the permission level in the sharing settings.

---

### "Token expired" / authentication failure

**Fix:**
```bash
gog auth remove owner@company.com
gog auth add owner@company.com --services calendar
# Re-run the OAuth flow
```

---

### Agent can read but not write (events show up but create fails)

**Cause:** Either wrong permission level, or the OAuth scope granted was read-only.

**Fix:**
1. Check share permission (Step 1) — must be "Make changes to events"
2. Re-authenticate with explicit write scope: `gog auth add owner@company.com --services calendar`

---

### Multiple calendars (work + personal)

If the owner has separate work and personal Google accounts:

```bash
# Add both accounts
gog auth add work@company.com --services calendar
gog auth add personal@gmail.com --services calendar

# List available calendars for each
GOG_ACCOUNT=work@company.com gog calendar list
GOG_ACCOUNT=personal@gmail.com gog calendar list

# Use specific calendar ID instead of "primary"
GOG_ACCOUNT=work@company.com gog calendar create CALENDAR_ID \
  --summary "Meeting" \
  --start "2026-04-02T10:00:00+00:00" \
  --end "2026-04-02T11:00:00+00:00"
```

**Note:** "primary" always refers to the main calendar of the specified account.

---

### Google Workspace account with domain restrictions

**Symptom:** Sharing invitation fails or agent can't authenticate.

**Fix:** Owner asks their Google Workspace admin to:
- Allow calendar sharing with external accounts
- Allow OAuth for third-party apps

This is an admin-level change in Google Admin Console.

---

### macOS date command incompatibility

The `date -d` flag is Linux-only. On macOS use `-v`:
```bash
# Linux
date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%SZ

# macOS
date -u -v+1H +%Y-%m-%dT%H:%M:%SZ
```

The test script above handles both automatically.

---

## Verification Checklist

- [ ] Owner has shared calendar with the agent email
- [ ] Permission level is "Make changes to events" (not read-only)
- [ ] Agent has added owner's account via `gog auth add`
- [ ] `gog auth list` shows owner's account with calendar service
- [ ] Test event created successfully in owner's calendar
- [ ] Test event deleted after verification
- [ ] Agent uses `GOG_ACCOUNT=owner@company.com` for all calendar operations

---

## Useful Commands

```bash
# List all authenticated accounts
gog auth list

# List available calendars for owner
GOG_ACCOUNT=owner@company.com gog calendar list

# List calendar events (next 7 days)
GOG_ACCOUNT=owner@company.com gog calendar events primary \
  --from $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --to $(date -u -d '+7 days' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v+7d +%Y-%m-%dT%H:%M:%SZ)

# Create event with attendees
GOG_ACCOUNT=owner@company.com gog calendar create primary \
  --summary "Meeting title" \
  --start "2026-04-02T10:00:00+00:00" \
  --end "2026-04-02T11:00:00+00:00" \
  --attendees "attendee@company.com"

# Delete event
GOG_ACCOUNT=owner@company.com gog calendar delete primary EVENT_ID

# Remove an authenticated account
gog auth remove owner@company.com
```

---

## Model Guidance

Calendar setup is a procedural task — any LLM can follow these steps. However:
- If the owner describes a complex issue (e.g. organizational restrictions, multi-domain setups), a more capable model will reason through it more reliably.
- For routine authentication checks and event creation, lightweight models are sufficient.
