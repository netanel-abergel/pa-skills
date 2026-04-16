---
name: skill-master
requires_skills:
  - skill-analytics
description: "Skill routing. Loaded at startup. For full skill library, decision tree, and workflows see REFERENCE.md."
---

# Skill Master

## How to Use
1. Read the request
2. Match in **Quick Lookup** below
3. Not found? Read `skills/skill-master/REFERENCE.md` for decision tree
4. Log the selection (see Analytics below), then load that skill's SKILL.md

Do not improvise. No match and REFERENCE.md doesn't help? Ask the owner.

## Production Rules (Always Active)
- React 👍 when receiving task from owner, ✅ when done
- "my pleasure / you're welcome" when anyone says "thank you"
- NO_REPLY for casual PA acks (thumbs up, "got it", "thank you") unless directly asked
- PA contacts: read from `PA_LIST.md`
- Google Calendar: use `/opt/ocana/openclaw/.gog/credentials.json` (NOT gog CLI)

## Analytics — Log Every Skill Use
```bash
echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"skill\":\"SKILL_NAME\",\"trigger\":\"TRIGGER\",\"context\":\"CONTEXT\"}" \
  >> /opt/ocana/openclaw/workspace/data/skill-analytics.jsonl
```

## Quick Lookup

| If the owner says... | Use skill |
|---|---|
| "who is X" / "phone for X" / "email of X" / "address of X" | contact-list |
| "PA of X" / "X's PA" / "JID of X" | contact-list |
| "add contact" / "update contact" | contact-list |
| "schedule a meeting" / "meeting notes" / "action items" | meetings |
| "what's on my calendar" / "morning briefing" | owner-briefing |
| "billing error" / "API out of credits" | billing-monitor |
| "connect calendar" / "connect Gmail" | calendar-setup |
| "set up a new PA" / "onboard agent" | pa-onboarding |
| "personal trainer" / "client check-in" / "workout program" / "fitness clients" | personal-trainer |
| "monday.com" / "create board item" / "track this" | monday-for-agents |
| "backup workspace" / "push to git" / "update openclaw" | pa-maintenance |
| "save this" / "where to save" | storage-router |
| "token usage" / "how much did today cost" | usage-costs |
| "what was discussed in [group]" | heleni-whatsapp |
| "search past messages" / "what did X say" | chat-history-local |
| "skill usage" / "skill stats" | skill-analytics |
| "security check" / "health check" | self-monitor |
| "PA network status" / "how are PAs doing" | supervisor |
| "how am I doing" / "run eval" | eval |
| "summarize YouTube video" | youtube-watcher |
| "compact memory" / "organize memory" | memory-tiering |
| "reduce token costs" / "optimize costs" | openclaw-token-optimizer |
| "CRM update" / "pre-meeting brief" | personal-crm |
| "research X" / "find out about X" | research-synthesizer |
| "should I reply?" | silence-strategy |
| "transcribe voice message" | whatsapp-voice |
| Said "I'll send" / "I'll report" in a reply | commitment-tracker |
| "I made a mistake" / "owner corrected me" | self-learning |
| "find new skill ideas" | skill-scout |

> **Storage rule:** Before saving content, run `storage-router`. Research -> monday.com. State/config -> local.

> **Privacy review (before push):** Scan for internal names, phone numbers, JIDs, board IDs. Replace with placeholders.

> **Skill count:** 29 active. Sweet spot: 15-25. Above 30 = routing breaks.
