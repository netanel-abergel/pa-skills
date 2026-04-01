---
name: skill-scout
description: "Daily automated skill discovery — searches the web for new OpenClaw skills, PA automation ideas, and AI agent capabilities, then delivers a curated list of recommendations to the admin. Use when: running the daily discovery cron job, asked for new skill ideas, or when looking for inspiration to expand the skill library."
---

# Skill Scout

Automatically discovers new skill ideas from the web daily and delivers them to the admin.

---

## What It Does

Every day, Skill Scout:
1. Searches ClawHub, GitHub, Reddit, and AI communities for new OpenClaw skills and automation ideas
2. Filters for skills relevant to PA workflows
3. Scores each idea by potential impact
4. Delivers a curated digest to the admin

---

## Daily Search Queries

Run these searches and aggregate results:

```bash
# ClawHub new skills
web_search("site:clawhub.ai new skills this week")
web_search("clawhub.ai PA agent productivity skills")

# GitHub
web_search("github openclaw skills new 2026")
web_search("github site:github.com openclaw SKILL.md")

# Communities
web_search("reddit r/openclaw new skill ideas")
web_search("site:dev.to openclaw agent automation")

# General PA automation ideas
web_search("AI personal assistant automation ideas 2026")
web_search("openclaw agent productivity workflows new")
```

---

## Scoring New Ideas

Score each idea 1–5 on:

| Criterion | Weight |
|---|---|
| PA relevance (scheduling, email, meetings, monitoring) | ×3 |
| Implementation effort (lower = better) | ×2 |
| Not already in skill library | ×2 |
| Community interest (stars, upvotes) | ×1 |

**Priority tiers:**
- 🔴 Score 35+ → Build immediately
- 🟡 Score 20–34 → Add to backlog
- 🟢 Score <20 → Log for reference

---

## Output Format

```
🔍 Skill Scout Daily Digest — YYYY-MM-DD

🔴 BUILD NOW
• [Skill Name] — [1-line description]
  Source: [URL]
  Why: [What problem it solves]
  Effort: Low/Medium/High

🟡 BACKLOG
• [Skill Name] — [1-line description]
  Source: [URL]

🟢 FYI
• [Skill Name] — [1-line description]

📦 Already have: [skills from results that we already built]

Next check: [tomorrow's date]
```

---

## Implementation

### The Scout Script

```python
import datetime

# Skills we already have — skip these in results
EXISTING_SKILLS = [
    "ai-pa", "billing-monitor", "calendar-setup", "meeting-scheduler",
    "monday-workspace", "openclaw-email-orientation", "owner-briefing",
    "pa-eval", "pa-onboarding", "pa-status", "self-learning",
    "skill-master", "skill-scout", "spawn-subagent", "whatsapp-diagnostics"
]

SEARCH_QUERIES = [
    "clawhub.ai new skills this week site:clawhub.ai",
    "openclaw skills github new 2026",
    "reddit r/openclaw skill ideas",
    "AI personal assistant automation workflows 2026",
    "openclaw agent productivity new"
]

# Run each query, collect results
results = []
for query in SEARCH_QUERIES:
    # Use web_search tool
    pass  # Agent fills in via web_search tool calls

# Filter, score, and format digest
today = datetime.date.today().isoformat()
digest_path = f"~/.openclaw/workspace/.learnings/skill-scout/{today}.md"

# Save and deliver
```

### Running the Scout

The agent runs this as a task:

```
1. Run all search queries using web_search tool
2. For each result: extract skill name, description, URL
3. Check against EXISTING_SKILLS list
4. Score each new idea (1–5 per criterion)
5. Format the digest
6. Save to .learnings/skill-scout/YYYY-MM-DD.md
7. Send digest to admin via WhatsApp
```

---

## Cron Configuration

```json
{
  "jobs": [
    {
      "id": "skill-scout",
      "schedule": "0 8 * * 1",
      "timezone": "UTC",
      "task": "Run skill-scout: search for new OpenClaw skill ideas, score them, and send a digest to the admin with recommendations for what to build next.",
      "delivery": {
        "mode": "message",
        "channel": "whatsapp",
        "to": "ADMIN_PHONE"
      }
    }
  ]
}
```

- Runs **every Monday at 08:00 UTC** (weekly is enough — daily is too noisy)
- Change to `"0 8 * * *"` for daily

---

## Sources to Monitor

| Source | What to Find |
|---|---|
| [clawhub.ai](https://clawhub.ai) | New published skills |
| [github.com/topics/openclaw](https://github.com/topics/openclaw) | Community-built skills |
| [reddit.com/r/openclaw](https://reddit.com/r/openclaw) | Ideas and requests |
| [dev.to](https://dev.to) + openclaw tag | Tutorials with new patterns |
| [lobehub.com/skills](https://lobehub.com/skills) | Skill marketplace mirror |
| HN "Ask HN" AI agent threads | Bleeding-edge automation ideas |

---

## Backlog Management

Save all ideas (even low-scored) to a rolling backlog:

```bash
BACKLOG="~/.openclaw/workspace/.learnings/skill-scout/backlog.md"

# Add new idea
echo "## [$(date +%Y-%m-%d)] $SKILL_NAME\n- Source: $URL\n- Score: $SCORE\n- Notes: $NOTES\n" >> $BACKLOG

# Review backlog monthly
cat $BACKLOG | grep -A4 "Score: [4-5]"
```

---

## Model Notes

- Any model can run the search queries
- A medium+ model is needed for scoring and summarization
- Use spawn-subagent to run this non-blocking in the background

```python
sessions_spawn(
    task="Run skill-scout: search for new OpenClaw skill ideas this week, score them, format a digest, save to .learnings/skill-scout/YYYY-MM-DD.md, and print the digest to stdout.",
    mode="run",
    runtime="subagent",
    runTimeoutSeconds=180
    # Optionally override model: model="your-provider/your-capable-model"
)
```
