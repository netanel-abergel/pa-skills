---
name: pa-onboarding
description: "Step-by-step onboarding guide for setting up a new AI Personal Assistant on OpenClaw. Use when: a new PA is being created, someone asks how to set up an agent, or guiding a user through the full setup process from account creation to first response."
---

# PA Onboarding Skill

## Minimum Model
Any model. This is a procedural guide — follow steps in order.

---

## Rules

- **Give one step at a time.** Do not dump the full guide upfront.
- **Confirm each step before moving on.** Do not assume it worked.
- **Never say something is done unless you verified it.**
- **Do not start integrations** (calendar, monday) before the agent is responding to messages.

If owner says "what's next?" → give only the single next step.
If owner says "I'm stuck on step X" → troubleshoot step X, do not move on.
If owner asks "can you do it for me?" → reply: "I can guide you — most steps require your action (QR scan, calendar share, etc.)"
If owner asks "how long will this take?" → reply: "Phase 1 takes 20–30 min. Integrations another 15–20 min."

---

## Owner Interaction Signals (Teach This Early)

The agent must learn these signals from day one:

| Signal | Meaning | Agent action |
|---|---|---|
| Any task request | Owner delegated a task | React 👍 immediately, ✅ when done |
| 👍 from owner | Good job | Log positive feedback |
| 👄 from owner | Poor result | Fix and log the lesson |

**Critical rules to cover during onboarding:**
- 👍 before starting any task, ✅ when complete — in every DM with the owner, no exceptions
- Never ask the owner "did you mean X?" if the answer is inferable — execute and let them correct
- When owner asks to check on someone: contact that person, then report back to the owner what they said. Never ask the owner instead of the person.
- Never include the owner's name or internal framing inside messages to third parties (PAs, contacts, vendors)

---

## Phase 1 — Account & Agent (Do This First)

### Step 1: Create Agent Account
- Go to the agent signup page (for monday.com orgs: [monday.com/agents-signup](https://monday.com/agents-signup)).
- Sign in with organization SSO.
- Create the agent and give it a name.

### Step 2: Get a Phone Number
- The agent needs a dedicated phone number for WhatsApp.
- Use Airalo eSIM (or similar) — must support SMS, not data-only.
- Cost: ~$5–15/month.

### Step 3: Install WhatsApp Business
- Download **WhatsApp Business** (not regular WhatsApp).
- Register the new phone number.
- Complete SMS verification.

### Step 4: Connect WhatsApp to Agent
1. Open OpenClaw platform → Agent Settings → Channels → WhatsApp.
2. Click Connect → scan QR code with WhatsApp Business app.
3. Wait 30 seconds for status to show "Connected and listening."

### Step 5: Verify the Agent Responds
- Send a test message to the agent's number.
- Confirm you get a reply within 30 seconds.
- **If no reply:** Stop here. Follow the `whatsapp-diagnostics` skill before continuing.

✅ **Phase 1 complete when the agent responds to messages.**

---

## Phase 2 — Integrations

**Only start Phase 2 after Phase 1 is fully working.**

### Step 6: Connect Google Calendar
- Owner shares their calendar with the agent email.
- Agent runs:
  ```bash
  gog auth add owner@company.com --services calendar
  ```
- Test that the agent can create events.
- Full guide: see `calendar-setup` skill.

### Step 7: Connect monday.com
1. Create a monday.com account for the agent (use org signup URL).
2. Generate API token: avatar → Developers → My Access Tokens → Copy.
3. Save the token:
   ```bash
   echo "YOUR_TOKEN" > ~/.credentials/monday-api-token.txt
   ```
4. (Optional) Set up monday MCP for natural language operations.
5. Full guide: see `monday-workspace` skill.

### Step 8: Set Up Email Access (Optional)
```bash
# Authenticate gog with Gmail and other services
gog auth add owner@company.com --services gmail,drive,contacts

# Test it works
GOG_ACCOUNT=owner@company.com gog gmail search 'is:unread' --max 5
```
Full guide: see `openclaw-email-orientation` skill.

---

## Phase 3 — Configuration

### Step 9: Configure SOUL.md

Key things to include:
- Owner's name and communication style.
- Work hours and timezone.
- What to act on autonomously vs. what requires permission.
- Topics to proactively monitor.

### Step 10: Schedule Morning Briefing (Optional)
- Cron job at 07:30 owner's timezone, Monday–Friday.
- Sends: meetings, urgent emails, open tasks.
- Full guide: see `owner-briefing` skill.

### Step 11: Add to PA Network Directory
- Update `data/pa-directory.json` with new PA details.
- Announce in the PA coordination group.

---

## Common Issues

| Issue | Likely Cause | Fix |
|---|---|---|
| Agent doesn't respond | WhatsApp not properly linked | Re-scan QR code |
| Messages count = 0 | Gateway ingest issue | Run `openclaw gateway restart` |
| Calendar connected but read-only | Wrong share permission | Owner re-shares with "Make changes" |
| Billing error | API key out of credits | Top up or switch model |
| eSIM not activating | Data-only plan | Get SMS-capable plan |

---

## Onboarding Checklist (Mandatory — Not Active Until Complete)

פעיל רשמי = עבר כל הסעיפים המסומנים ִב-★. השאר אופציונלי.

```
★ [ ] Agent responds to test message (WhatsApp working)
★ [ ] Skills installed from pa-skills repo (min: owner-briefing, proactive-pa, self-monitor, billing-monitor, skill-master, supervisor)
★ [ ] Google Calendar connected (write access) — use share-to-PA-email if gog CLI fails
★ [ ] Morning briefing cron scheduled (08:00 owner timezone)
★ [ ] HEARTBEAT.md updated with concrete proactivity triggers
★ [ ] Added to PA network directory (PA_LIST.md)
★ [ ] Added to PA Onboarding WhatsApp group
★ [ ] Self-introduced in PA Onboarding group
  [ ] monday.com token saved (optional)
  [ ] Email/Gmail access (optional)
  [ ] git backup configured (optional)
  [ ] usage-costs skill installed + daily-token-report cron configured (recommended)
```

**בלא ★ הרשימה מלאה — PA לא נחשבת active.**

---

## Cost Tips

- **Cheap:** Onboarding is procedural — any small model works.
- **Avoid:** Do not attempt all phases simultaneously — go in order.
- **Small model OK:** Use a medium model only if SOUL.md customization needs nuanced tone matching.

---

## Lessons from Production (2026-04-05 — Yennefar & Laika Onboarding)

1. **Calendar setup = Day 1, not Day 5** — every PA hits the same wall (gog CLI doesn't work on server). Add it to the mandatory checklist early. Workaround: share calendar to PA email (`agent_email@ocana.ai`) with "Make changes to events" permission.

2. **Skills don't install themselves** — PAs will confirm they completed tasks without actually doing them. Always verify: ask for line count, file listing, or a functional test. Don't accept "done" without evidence.

3. **Group membership requires owner approval** — privacy-disciplined PAs (correctly) won't join groups without explicit owner authorization. Don't send invite links directly. Flow: Heleni asks Netanel → Netanel contacts the PA's owner → owner authorizes → PA joins.

4. **invite link vs. manual add** — PAs cannot click links. Only humans can join via link. To add a PA to a group: admin must add the phone number manually from their phone.

5. **PA-to-PA mentoring works** — sending skill files + tips directly from one PA to another (Heleni → Yennefar) is effective and scalable. Codify this as the standard onboarding assist pattern.

6. **Mandatory checklist, not recommendations** — without a gate, PAs stay half-configured indefinitely. The checklist above (★ items) is the definition of "active". Use it as the quality gate.

## Lessons from Production (2026-04-05 — Cost Optimization Survey)

1. **0 out of 14 PAs tracked costs** — cost visibility is a blind spot across the entire network. Install `usage-costs` skill as standard onboarding (not optional). Add `daily-token-report` cron from day 1.

2. **Google/OpenAI agents need different cost tracking** — the jsonl cost extraction script only works for Anthropic Claude. Edward (Gemini) and Laika (GPT) had no cost data. For non-Anthropic agents, direct the owner to the provider billing dashboard.

3. **Most PAs use `/status` for tokens, not dollars** — tokens alone are misleading (cache reads are cheap, cache writes are expensive). Always track `$` cost, not just token count.

4. **thinkingDefault=off + Haiku for simple crons = significant savings** — 5 simple crons migrated from Sonnet+thinking to Haiku+off. Estimated ~$2–4/day saving per agent. Apply this pattern to all new agents from day 1.

## Lessons from Production (2026-04-02)

Lessons learned from running PAs in production. Future agents setting up a new PA should apply these from day 1.

1. **Skill count matters** — the sweet spot is 28–32 active skills. Start lean and add a new skill only when there's a clear, recurring trigger phrase that no existing skill covers. Above 40 skills, routing breaks down and the agent starts misfiring. Less is more.

2. **HOT.md** — create this file from day 1. Max 20 lines. It's not documentation — it's the short list of rules the agent keeps breaking. If you find yourself correcting the same behavior twice, it belongs in HOT.md. Review it at the start of every session.

3. **SOUL.md vs Skills** — universal behavioral rules (temperature selection, proactivity level, tone, response length) go in SOUL.md and apply everywhere. Skills are for triggered, domain-specific workflows only. Don't put behavioral rules inside a skill — they won't apply globally.

4. **Diagnostics are appendices** — never create a standalone diagnostics skill (e.g. `whatsapp-diagnostics`). Instead, add a troubleshooting section at the bottom of the parent skill (e.g. `whatsapp`). Standalone diagnostics skills fragment routing and add noise to the skill library.

5. **DEPRECATED.md discipline** — when you merge or retire a skill, always write a tombstone file explaining why. Include: what it merged into, the date, the reason, and the lesson. Future agents (and humans) will thank you. Without tombstones, retired skills become ghost entries that confuse routing.

6. **pa-skills repo** — before building a skill from scratch, check https://github.com/netanel-abergel/pa-skills for a curated starting library. It reflects all the above lessons and provides production-ready skill templates for the most common PA workflows.
