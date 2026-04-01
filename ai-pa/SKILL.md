---
name: ai-pa
description: AI Personal Assistant network skill for Ocana agents. Use when: contacting another PA, sending a message to an owner, scheduling a meeting, finding a PA's phone number, looking up group JIDs, understanding who owns which PA, checking roles/titles, or performing any cross-PA coordination task. Contains the full PA network directory, group JIDs, owner contacts, task templates, and workflows for scheduling, email, and outreach.
---

# AI-PA Network Skill

The definitive reference and workflow guide for operating within the Ocana PA network at monday.com.

---

## PA Directory

| PA Name | PA Phone | Owner | Owner Phone | Owner Role | Status |
|---|---|---|---|---|---|
| Heleni | +972555193968 | Netanel Abergel | +972548834688 | Director R&D | ✅ Active |
| Selena Vox | +972522486583 | Daniel Lereya | +972545911021 | CTPO | ✅ Active |
| Kira (Sienna Lima) | +972537210135 | Orly Yitzhaki | +972529426200 | VP Product | ✅ Active |
| Adam (Kian Rowe) | +972537209898 | Lilach | — | monday.com Leadership | ✅ Active |
| Hagit (Nia Calder) | +972537210098 | Sergei Liakhovetsky | +972526148968 | VP R&D | ✅ Active |
| Jatvin (Jarvis) | +972555193914 | Liron Streichman | — | VP R&D | ✅ Active |
| Drew | +972555193909 | Dor Yehuda | +972585555966 | monday.com | ✅ Active |
| Edward | +972555193939 | Ido Karlen | — | Director / Infra Lead | ✅ Active |
| Martha | +972559317594 | Ohad | — | monday.com Leadership | ✅ Active |
| Midgee | +972529086394 | Doron Sinai | +972547691235 | monday.com | ✅ Active |
| Janet | +972555193907 | Gabriel Amram | +972505250303 | monday.com | ✅ Active |
| Jeffrey (Smith) | +972555193913 | Ziv Monday | +972535310971 | monday.com | ✅ Active |
| Ruth | +972555193921 | Tomer Brook | +972525290870 | monday.com | ✅ Active |
| Dorbot | +972559434156 | Dor Cohen | +972546100066 | monday.com | ✅ Active |
| Alfred | +972555193891 | Guy Atzmon | +972542010180 | VP Product Design | ✅ Active |
| Laika | +19406175722 | Omri Cohen | +972547756778 | VP Product | ✅ Active |
| Valkirie | — | Ruslan Semenov | +447939664974 | Director R&D | 🔧 Setup |
| Yennefar | +972529382314 | Neta Fishman | +972509666833 | Program Manager | ✅ Active |

---

## Key Group JIDs (WhatsApp)

| Group | JID |
|---|---|
| PA Onboarding | 120363408613668489@g.us |
| Monday PA Team | 120363422865795623@g.us |
| Builders Leadership | 120363183026390862@g.us |
| monday Internal AI | 120363407499862433@g.us |
| Family | 120363425247194027@g.us |
| Heleni + Alfred + Guy | 120363423770223542@g.us |

---

## Contacts Without PA (Pending / Interested)

| Name | Phone | Role | Notes |
|---|---|---|---|
| Eran Huberman | +972549222625 | Director | Interested, directed to ocana.ai |
| Michal | +972543331939 | Director of Product Operations | PA: Drake, in process |
| Kate Nir | +972526610247 | Agent Builder | — |
| Inbal Rosenshtock | +972549982282 | monday.com | Calendar issue |

---

## Task Templates

### Scheduling a Meeting (PA → PA)

When your owner wants to meet with someone:

1. Identify the other party's PA from the directory above
2. Contact the PA directly (not the owner):
   > "Hey [PA name], [your owner] would like to schedule a meeting with [their owner]. Is [proposed time / ask for availability]?"
3. Confirm time, send calendar invite via `gog calendar create`
4. Update your owner with confirmation

**Never contact the other owner directly for scheduling** — always go through their PA.

### Scheduling a Meeting (Owner Request → Calendar)

```bash
# Create event on owner's calendar
gog calendar create primary \
  --summary "Meeting: [Owner] + [Other Party]" \
  --start "2026-04-02T10:00:00+03:00" \
  --end "2026-04-02T11:00:00+03:00" \
  --attendees "other@monday.com"
```

### Sending Email on Owner's Behalf

```bash
# Send via gog
GOG_ACCOUNT=owner@monday.com gog gmail send \
  --to "recipient@company.com" \
  --subject "Subject here" \
  --body "Email body here"
```

Always confirm with owner before sending external emails.

### Broadcasting to All PAs

Send to PA Onboarding group (reaches all PAs):
- JID: `120363408613668489@g.us`
- Use WhatsApp message tool with `target: 120363408613668489@g.us`

Or send individual DMs using phone numbers from the directory above.

### Contacting an Owner Directly

Only when:
- Their PA is unavailable/unresponsive
- Urgent matter that can't wait
- Explicitly instructed by your owner

**Note:** Some owners prefer not to receive PA-to-owner messages (e.g. Daniel Lereya — contact Selena instead).

---

## Roles & Titles Reference (monday.com)

| Person | Title |
|---|---|
| Netanel Abergel | Director of R&D |
| Daniel Lereya | CTPO |
| Orly Yitzhaki | VP Product |
| Sergei Liakhovetsky | VP R&D |
| Omri Cohen | VP Product |
| Guy Atzmon | VP Product Design |
| Ruslan Semenov | Director R&D |
| Eran Huberman | Director |
| Ido Karlen | Director / Infra Lead |
| Doron Sinai | monday.com |
| Gabriel Amram | monday.com |
| Ziv Monday | monday.com |
| Dor Cohen | monday.com |
| Dor Yehuda | monday.com |
| Tomer Brook | monday.com |

---

## Operating Rules

- **Always contact PA, not owner** — for scheduling, messages, coordination
- **Exception:** Urgent/owner preference/PA unavailable → contact owner directly with context
- **Daniel Lereya** — does not want PA-mediated messages. Contact Selena or Netanel directly.
- **Dorbot/Dor Cohen** — contact Dorbot directly, not Dor
- **Group broadcasts** → use PA Onboarding group JID
- **Leadership-only matters** → use Builders Leadership JID
- **monday.com account signup for agents** → https://monday.com/agents-signup

---

## Billing & Model Issues

When a PA reports a billing error:
1. Notify the PA's owner immediately
2. Notify Netanel (+972548834688) — he manages the Anthropic budget
3. Workaround: suggest switching to a non-Claude model temporarily in ocana.ai settings

Current known issue (April 2026): Claude budget shared across 200+ agents — runs out quickly. Claude access may be restricted to Leadership only.

---

## Onboarding a New PA

Full flow:
1. Direct to [monday.com/agents-signup](https://monday.com/agents-signup) for monday account
2. Sign in to ocana.ai via Okta
3. Create agent, choose name
4. Get phone number (Airalo eSIM recommended)
5. Install WhatsApp Business, verify number
6. Connect WhatsApp to agent
7. Verify agent responds
8. Connect Google Calendar (see ocana-email-orientation skill)
9. Connect monday.com (see monday-workspace skill)

Self-setup only — PA does not set up on behalf of others.

---

## Quick Lookup

**"Who is X's PA?"** → Check PA Directory, Owner column
**"What's PA X's phone?"** → Check PA Directory, PA Phone column
**"What group JID for PA broadcasts?"** → 120363408613668489@g.us
**"How do I schedule a meeting?"** → See Task Templates → Scheduling
**"Who has billing issues?"** → Dorbot (Dor Cohen), Janet (Gabriel Amram), Selena (Daniel Lereya) — April 2026
