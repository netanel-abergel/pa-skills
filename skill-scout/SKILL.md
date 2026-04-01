---
name: skill-scout
description: "Daily automated skill discovery — searches the web for new OpenClaw skills, PA automation ideas, and AI agent capabilities, then delivers a curated list of recommendations to the admin. Use when: running the daily discovery cron job, asked for new skill ideas, or when looking for inspiration to expand the skill library."
---

# Skill Scout

## Minimum Model
Medium model for scoring and summarization. Small model can run searches.

---

## What It Does

Once a week, Skill Scout:
1. Searches for new OpenClaw skills and PA automation ideas.
2. Filters for skills relevant to PA workflows.
3. Scores each idea by potential impact.
4. Delivers a curated digest to the admin.

---

## Step-by-Step Process

1. Run all search queries using `web_search`.
2. For each result:
   - Extract skill name, description, and URL.
   - Check if it's already in the existing skills list (see below). If yes, skip it.
   - If new: score it using the criteria below.
3. Sort results by score (descending).
4. Format the digest.
5. Save digest to `.learnings/skill-scout/YYYY-MM-DD.md`.
6. Send digest to admin via WhatsApp.

---

## Search Queries

Run these using the `web_search` tool:

```
clawhub.ai new skills this week site:clawhub.ai
openclaw skills github new 2026
reddit r/openclaw skill ideas
AI personal assistant automation workflows 2026
github site:github.com openclaw SKILL.md
```

---

## Scoring Criteria

Score each idea on these weighted criteria:

| Criterion | Weight |
|---|---|
| Relevant to PA workflows (scheduling, email, meetings, monitoring) | ×3 |
| Low implementation effort | ×2 |
| Not already in skill library | ×2 |
| Community interest (stars, upvotes) | ×1 |

**Priority tiers:**
- 🔴 35+ points → Recommend building now
- 🟡 20–34 → Add to backlog
- 🟢 <20 → Log for reference

**Existing skills (exclude from results):**
```
ai-pa, billing-monitor, calendar-setup, git-backup, meeting-scheduler,
monday-workspace, openclaw-email-orientation, owner-briefing, pa-eval,
pa-onboarding, pa-status, self-learning, skill-master, skill-scout,
spawn-subagent, whatsapp-diagnostics, whatsapp-memory
```

---

## Output Format

```
🔍 Skill Scout Digest — YYYY-MM-DD

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

📦 Already have: [skills found in results that we already built]
```

---

## Save the Digest

```bash
#!/bin/bash
set -e

SCOUT_DIR="$HOME/.openclaw/workspace/.learnings/skill-scout"
mkdir -p "$SCOUT_DIR"

DATE=$(date +%Y-%m-%d)
OUTPUT_FILE="$SCOUT_DIR/$DATE.md"

# Write digest content to file (replace with actual digest)
cat > "$OUTPUT_FILE" << 'EOF'
[digest content here]
EOF

echo "Saved to $OUTPUT_FILE"
```

---

## Backlog Management

```bash
#!/bin/bash
set -e

BACKLOG="$HOME/.openclaw/workspace/.learnings/skill-scout/backlog.md"
DATE=$(date +%Y-%m-%d)

# Add a new idea to the backlog
cat >> "$BACKLOG" << EOF

## [$DATE] $SKILL_NAME
- Source: $URL
- Score: $SCORE
- Notes: $NOTES
EOF

# View high-priority backlog items
grep -A4 "Score: [4-5]" "$BACKLOG"
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
      "task": "Run skill-scout: search for new OpenClaw skill ideas this week, score them, format a digest, save to .learnings/skill-scout/YYYY-MM-DD.md, and send to admin.",
      "delivery": {
        "mode": "message",
        "channel": "whatsapp",
        "to": "ADMIN_PHONE"
      }
    }
  ]
}
```

Runs **every Monday at 08:00 UTC**. Change to `"0 8 * * *"` for daily (not recommended — too noisy).

---

## Sources to Check

| Source | What to Find |
|---|---|
| [clawhub.ai](https://clawhub.ai) | New published skills |
| [github.com/topics/openclaw](https://github.com/topics/openclaw) | Community-built skills |
| [reddit.com/r/openclaw](https://reddit.com/r/openclaw) | Feature requests and ideas |
| [dev.to](https://dev.to) + openclaw tag | Tutorials with new patterns |
| Hacker News AI agent threads | Bleeding-edge automation ideas |

---

## Running as a Subagent (Recommended)

Skill scout involves multiple web searches and can take 2+ minutes. Run non-blocking:

```python
sessions_spawn(
    task="""
    Run skill-scout:
    1. Run these web searches: [list queries above]
    2. Score each new skill idea (exclude existing skills listed above)
    3. Format the digest
    4. Save to .learnings/skill-scout/YYYY-MM-DD.md
    5. Print the digest to stdout
    """,
    mode="run",
    runtime="subagent",
    runTimeoutSeconds=180
)
```

---

## Cost Tips

- **Expensive:** Multiple web searches — use a medium model for scoring, not a large one.
- **Cheap:** Saving the digest to a file — no model tokens needed.
- **Batch:** Run all 5 searches in one subagent session, not 5 separate sessions.
- **Weekly, not daily:** Daily is too noisy and wastes tokens. Weekly is sufficient.
