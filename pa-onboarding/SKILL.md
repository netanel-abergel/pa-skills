---
name: pa-onboarding
description: "Step-by-step onboarding guide for setting up a new AI Personal Assistant on OpenClaw. Use when: a new PA is being created, someone asks how to set up an agent, or guiding a user through the full setup process from account creation to first response."
---

# PA Onboarding Skill

Complete setup guide for a new AI Personal Assistant on OpenClaw.

---

## Golden Rules

- ✅ Give **one next step at a time** — don't dump the full guide upfront
- ✅ Confirm each step is complete before moving to the next
- ❌ Never say something is done unless you've verified it
- ❌ Don't start integrations (calendar, monday) before the agent is responding

---

## Full Setup Flow

### Phase 1 — Account & Agent

**Step 1: Create agent account**
- Go to the agent signup page (e.g. monday.com/agents-signup for monday.com orgs)
- Sign in with your organization's SSO/Okta
- Create a new agent and give it a name

**Step 2: Get a phone number**
- The agent needs a dedicated phone number for WhatsApp
- Recommended: Airalo eSIM (supports activation via SMS)
- Ensure the plan supports SMS (not data-only)
- Cost: ~$5–15/month

**Step 3: Install WhatsApp Business**
- Download WhatsApp Business (not regular WhatsApp) on any device
- Register the new phone number
- Complete verification via SMS

**Step 4: Connect WhatsApp to agent**
- In OpenClaw platform → Agent Settings → Channels → WhatsApp
- Click Connect → scan QR code with WhatsApp Business
- Wait for status to show "Connected and listening"

**Step 5: Verify the agent responds**
- Send a test message to the agent's number
- Confirm you get a reply
- If no reply: see whatsapp-diagnostics skill

---

### Phase 2 — Integrations

Only start this phase after Phase 1 is complete and the agent is responding.

**Step 6: Connect Google Calendar**
- Owner shares their calendar with the agent email
- Agent authenticates: `gog auth add owner@company.com --services calendar`
- Test write access
- Full guide: see calendar-setup skill

**Step 7: Connect monday.com**
- Agent gets a monday.com account (use org-specific signup URL)
- Generate API token from Developer settings
- Save token: `echo TOKEN > ~/.credentials/monday-api-token.txt`
- Set up monday MCP for natural language board operations
- Full guide: see monday-workspace skill

**Step 8: Set up email access (optional)**
- `gog auth add owner@company.com --services gmail,drive,contacts`
- Test: `GOG_ACCOUNT=owner@company.com gog gmail search 'is:unread' --max 5`
- Full guide: see openclaw-email-orientation skill

---

### Phase 3 — Configuration

**Step 9: Configure SOUL.md**
Key rules to include:
- Owner's name and communication preferences
- Work hours and timezone
- Topics to proactively monitor
- What to ask before acting vs. what to do autonomously

**Step 10: Set up morning briefing (optional)**
- Configure cron job at 07:30 owner's timezone
- Sends: meetings, urgent emails, open tasks
- Full guide: see owner-briefing skill

**Step 11: Add to PA network directory**
- Update `data/pa-directory.json` with the new PA's details
- Announce in PA coordination group

---

## What to Say at Each Stage

**"What's next?"**
→ Give only the single next step

**"I'm stuck on step X"**
→ Troubleshoot that step before moving forward

**"Can you set it up for me?"**
→ "I can guide you through it, but each step requires your action (scanning QR, accepting calendar share, etc.)"

**"How long does this take?"**
→ "Phase 1 takes about 20–30 minutes. Integrations another 15–20 min."

---

## Common Issues

| Issue | Likely Cause | Fix |
|---|---|---|
| Agent doesn't respond after setup | WhatsApp not properly linked | Re-scan QR code |
| Messages=0 in dashboard | Gateway ingest issue | Run `openclaw gateway restart` |
| Calendar connected but read-only | Wrong share permission | Owner re-shares with "Make changes" |
| API billing error | Key out of credits | Top up or switch model |
| eSIM not activating | Data-only plan | Get SMS-capable plan |

---

## Onboarding Checklist

```
[ ] Agent account created
[ ] Phone number acquired
[ ] WhatsApp Business installed and registered
[ ] WhatsApp connected to agent
[ ] Agent responds to test message
[ ] Google Calendar connected with write access
[ ] monday.com account created and token saved
[ ] SOUL.md configured with owner preferences
[ ] Morning briefing scheduled (optional)
[ ] Added to PA network directory
[ ] Announced in PA coordination group
```

---

## Model Compatibility

This skill works with any LLM model capable of following multi-step instructions.

| Task | Minimum Model |
|---|---|
| Guiding through onboarding steps | Any |
| Troubleshooting WhatsApp issues | Small–Medium |
| Troubleshooting calendar/email access | Small–Medium |
| Customizing SOUL.md for the owner | Medium recommended (better tone/personalization) |

The onboarding process is primarily procedural — no model-specific features are required. Any model that can follow instructions and respond to user confirmations will work.

> **Note:** OpenClaw supports multiple LLM providers (Anthropic, OpenAI, Google, etc.). During account setup, the owner selects their preferred model provider. The onboarding steps are the same regardless of provider.
