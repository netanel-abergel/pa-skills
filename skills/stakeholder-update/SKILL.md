# stakeholder-update

Draft concise, structured stakeholder updates from raw operational context — incidents, blockers, progress notes, or ad-hoc summaries.

## When to Use
- Owner asks: "draft an update for the team", "send a status to stakeholders", "write a summary of what happened"
- After an incident or anomaly is resolved
- Before or after a meeting where a written update is needed
- Periodic operational summaries (weekly, end-of-sprint, etc.)

## What It Produces
A short, structured message with:
- **What happened** (1–2 sentences, factual)
- **Current status** (resolved / in-progress / monitoring)
- **Risk / impact** (who/what is affected, severity)
- **Next action** (one clear owner + deadline if known)
- **ETA** (if applicable)

## Instructions

### Step 1 — Gather context
Ask the owner (or read from memory/context files):
- What is the situation?
- Who is the audience? (team, management, customer, all-hands)
- What tone? (formal / casual / technical)
- Any specific risk or mitigation to highlight?

If context is already available (e.g., from a prior incident summary or heartbeat note), skip asking and draft directly.

### Step 2 — Draft
Use this template:

```
📋 Status Update — [topic] — [date]

*What happened:* [1–2 sentences, plain language]
*Status:* [Resolved ✅ / In Progress 🔄 / Monitoring 👀]
*Impact:* [Who or what was affected, severity]
*Risk:* [Remaining risk or "None — fully resolved"]
*Next action:* [Owner: NAME — action — by WHEN]
[Optional: ETA or follow-up note]
```

Adapt tone to audience:
- **Team/internal:** casual, direct, can use abbreviations
- **Management:** concise, outcome-focused, no jargon
- **Customer-facing:** empathetic, clear, avoid internal terms

### Step 3 — Confirm before sending
Always show the draft to the owner first. Say:
> "Here's the draft — want me to send it, adjust the tone, or change anything?"

Never send without explicit confirmation.

### Step 4 — Log
After the update is sent, note it in `memory/YYYY-MM-DD.md`:
```
- Sent stakeholder update: [topic] → [audience] at [time]
```

## Example
**Trigger:** "Draft an update for the team — the API was down for 20 minutes, it's fixed now"

**Output:**
```
📋 Status Update — API Outage — Apr 7, 2026

*What happened:* The production API was unavailable for ~20 minutes due to a misconfigured rate-limit rule deployed at 14:30.
*Status:* Resolved ✅
*Impact:* External API consumers experienced 503 errors. ~40 requests failed.
*Risk:* None — rollback applied, monitoring confirms stability.
*Next action:* Nia — add rate-limit validation to deploy checklist — by Apr 9
```

## Notes
- Keep under 150 words for async/chat delivery; longer for formal reports
- Default to internal/team tone if audience is unknown
- Never include credentials, internal IPs, or PII

## Credit
Contributed by Nia Calder (Sergei's PA), April 2026.
