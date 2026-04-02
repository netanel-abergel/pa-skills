---
name: skill-scout
description: "Daily automated skill discovery — scans memory files for unmet needs, searches the web for new OpenClaw skills, PA automation ideas, and AI agent capabilities, then delivers a curated digest to the admin. Use when: running the daily discovery cron job, asked for new skill ideas, or when looking for inspiration to expand the skill library."
---

# Skill Scout

## Minimum Model
Medium model for scoring and summarization.

---

## What It Does

Daily, Skill Scout:
1. **Gap Mining** — Scans memory files and HEARTBEAT.md for unmet needs and repeated manual tasks.
2. **Web Search** — Searches for new skills that address those gaps + general PA automation ideas.
3. **Dedup + Score** — Filters out already-installed skills, scores remaining by impact.
4. **URL Validation** — Verifies all URLs are real before including them.
5. **Digest Delivery** — Sends curated results to Netanel in group 120363407274831275@g.us.

---

## Step-by-Step Process

### Phase 1: Gap Mining (do this FIRST)

Before searching the web, scan internally:

1. Read `memory/` files from the last 7 days → look for:
   - Tasks marked as failed or blocked
   - Manual steps done repeatedly (e.g., "manually checked X", "had to do Y by hand")
   - Things Netanel complained about or asked for repeatedly
2. Read `HEARTBEAT.md` → look for todo items with no associated skill
3. Check `.learnings/skill-scout/backlog.md` → pending items from prior weeks

From this, generate a short list: "Gap → Skill type needed"

Example:
- "Netanel asked to summarize meeting 3x this week" → needs meeting-notetaker skill
- "Calendar check done manually" → smart-scheduler skill

### Phase 2: Dedup Check

Before searching, list all installed skills:
```bash
ls /opt/ocana/openclaw/workspace/skills/
```

Also check known existing list:
```
ai-pa, billing-monitor, calendar-setup, git-backup, meeting-scheduler,
monday-for-agents, openclaw-email-orientation, owner-briefing, pa-eval,
pa-onboarding, pa-status, self-learning, skill-master, skill-scout,
spawn-subagent, whatsapp-diagnostics, whatsapp, security-guardian,
dynamic-temperature, memory-tiering, self-monitor, supervisor, eval,
proactive-pa, hebrew-nikud, ai-meeting-notes, youtube-watcher,
chat-history, cross-group-awareness, clawddocs, devprocess, ownership,
self-improvement, self-reflection, ai-pa-browser, monday-for-agents,
openclaw-auto-updater, git-backup, skill-creator, calendar-setup
```

### Phase 3: Web Search

Run ALL these queries using `web_search`:

**Gap-targeted queries** (generated from Phase 1 gaps):
- Dynamic — based on what gaps were found. E.g.: `openclaw skill meeting notes transcription 2026`

**Fixed queries:**
```
site:clawhub.ai openclaw new skills 2026
openclaw skills github new 2026
site:clawskills.sh productivity personal assistant
AI personal assistant automation workflows 2026
firecrawl.dev openclaw skills blog
```

### Phase 4: Score Each Result

For each result found:
1. Skip if already in installed/known skills list
2. Score using:

| Criterion | Weight |
|---|---|
| Addresses a known gap from Phase 1 | ×3 |
| Relevant to PA workflows (scheduling, email, meetings, monitoring) | ×3 |
| Low implementation effort | ×2 |
| Not already in skill library | ×2 |
| Community interest (stars, upvotes, engagement) | ×1 |

Max possible: 44 points

**Priority tiers:**
- 🔴 35+ → BUILD NOW
- 🟡 20–34 → BACKLOG
- 🟢 <20 → FYI

### Phase 5: URL Validation

Before including any skill in the digest:
- Attempt to fetch the URL (web_fetch with short timeout)
- If 404 / error → mark as "unverified" and exclude from digest
- Only include URLs that returned 200

**Never hallucinate ClawHub or GitHub URLs.**

### Phase 6: Format and Deliver

Format digest (see Output Format below).

Save to: `/opt/ocana/openclaw/workspace/.learnings/skill-scout/YYYY-MM-DD.md`

Auto-append 🟡 BACKLOG items to: `/opt/ocana/openclaw/workspace/.learnings/skill-scout/backlog.md`

Send digest to WhatsApp group: `120363407274831275@g.us`

---

## Output Format

```
🔍 Skill Scout Digest — YYYY-MM-DD

🧩 GAPS IDENTIFIED (from memory scan)
• [Repeated task] → suggests [Skill type]
• [Blocked item] → suggests [Skill type]

🔴 BUILD NOW
• [Skill Name] — [1-line description]
  Source: [URL] ✅
  Why: [What problem it solves / which gap it closes]
  Effort: Low/Medium/High

🟡 BACKLOG (saved to backlog.md)
• [Skill Name] — [1-line description]
  Source: [URL] ✅

🟢 FYI
• [Skill Name] — [1-line description]

📦 Already have: [skills found in results that we already built]
🔗 All URLs verified ✅ / ⚠️ [N] unverified excluded
```

---

## Backlog Management

Auto-append 🟡 items to backlog:

```bash
BACKLOG="/opt/ocana/openclaw/workspace/.learnings/skill-scout/backlog.md"
DATE=$(date +%Y-%m-%d)
# Append each backlog item with date + score
```

---

## Cron Configuration

Daily at 08:00 Israel time (06:00 UTC):

```json
{
  "id": "skill-scout-daily",
  "schedule": "0 6 * * *",
  "timezone": "UTC",
  "task": "Run skill-scout: (1) Scan memory/ files from last 7 days and HEARTBEAT.md for unmet needs and repeated manual tasks — list gaps. (2) Dedup against installed skills. (3) Run web searches for new OpenClaw skills addressing those gaps. (4) Score and filter. (5) Validate URLs. (6) Format digest. (7) Save to .learnings/skill-scout/YYYY-MM-DD.md. (8) Append backlog items. (9) Send digest to WhatsApp group 120363407274831275@g.us.",
  "delivery": {
    "mode": "message",
    "channel": "whatsapp",
    "to": "120363407274831275@g.us"
  }
}
```

---

## Sources to Check

| Source | What to Find |
|---|---|
| [clawhub.ai](https://clawhub.ai) | New published skills |
| [clawskills.sh](https://clawskills.sh) | Curated community skills |
| [github.com/topics/openclaw](https://github.com/topics/openclaw) | Community-built skills |
| [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) | Categorized 5,400+ skills |
| [firecrawl.dev/blog](https://firecrawl.dev/blog) | Blog posts about OpenClaw skills |
| Hacker News AI agent threads | Bleeding-edge automation ideas |

---

## Running as a Subagent (Required)

Skill scout involves multiple steps and takes 2–3 minutes. Always run as subagent:

```python
sessions_spawn(
    task="""
    Run skill-scout daily digest:
    Phase 1: Scan /opt/ocana/openclaw/workspace/memory/ (last 7 days) and HEARTBEAT.md for gaps/unmet needs.
    Phase 2: Check installed skills in /opt/ocana/openclaw/workspace/skills/
    Phase 3: Run web searches (gap-targeted + fixed queries)
    Phase 4: Score results (skip already-installed)
    Phase 5: Validate URLs with web_fetch
    Phase 6: Format digest, save to .learnings/skill-scout/YYYY-MM-DD.md, append backlog
    Phase 7: Print full digest to stdout
    """,
    mode="run",
    runtime="subagent",
    runTimeoutSeconds=240
)
```

---

## Cost Tips

- Gap mining is free (file reads, no web calls)
- URL validation: one fetch per candidate — worth it to avoid hallucinated links
- Medium model for scoring only
- Daily is fine since gap-mining makes each run targeted and non-repetitive
