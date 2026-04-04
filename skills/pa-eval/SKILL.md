---
name: pa-eval
description: "Evaluate PA performance through structured scoring, owner feedback analysis, and behavioral benchmarking. Use when: conducting a weekly/monthly PA performance review, owner gives feedback (positive or negative), assessing response quality, or identifying areas for improvement."
---

# PA Eval Skill

## Load Local Context
```bash
CONTEXT_FILE="/opt/ocana/openclaw/workspace/skills/pa-eval/.context"
[ -f "$CONTEXT_FILE" ] && source "$CONTEXT_FILE"
# Then use: $OWNER_PHONE, $EVAL_DIR, $WORKSPACE, etc.
```

## Minimum Model
Any model for filling in templates. Use a medium model for trend analysis and recommendations.

---

## When to Run

- **Weekly self-eval:** Every 7 days. Run automatically.
- **On owner correction:** Log the correction immediately, then re-score the affected dimension.
- **Monthly report:** At the end of each month, aggregate all weekly evals.
- **On demand:** If owner asks "how am I doing?" → generate current eval on the spot.

---

## Scoring Dimensions

Score each 1–5:

| Dimension | What to Measure |
|---|---|
| **Execution** | Tasks completed without reminders |
| **Accuracy** | Results are correct and complete |
| **Speed** | Response time is fast |
| **Proactivity** | Acts without being asked |
| **Communication** | Concise and context-appropriate |
| **Memory** | Remembers context across sessions |
| **Tool Use** | Tools used correctly and efficiently |
| **Judgment** | Knows when to act vs. when to ask |

**Score meanings:**
- 5 = Consistently exceeds expectations
- 4 = Meets expectations with minor gaps
- 3 = Acceptable but basic
- 2 = Frequent gaps or errors
- 1 = Fails basic expectations

**Total:** Max 40 points.
Grade: A (36–40), B (28–35), C (20–27), D (<20)

---

## Weekly Self-Evaluation

Save to `.learnings/eval/YYYY-MM-DD.md`.

```markdown
# PA Weekly Eval — YYYY-MM-DD

## Scores

| Dimension | Score | Notes |
|---|---|---|
| Execution | /5 | |
| Accuracy | /5 | |
| Speed | /5 | |
| Proactivity | /5 | |
| Communication | /5 | |
| Memory | /5 | |
| Tool Use | /5 | |
| Judgment | /5 | |
| **TOTAL** | /40 | |

## Owner Feedback This Week

- Positive:
- Corrections:
- Complaints:

## Tasks Completed

-

## Tasks Failed or Incomplete

-

## What Went Well

-

## What to Improve

-

## Actions for Next Week

- [ ]
```

### Create the File

```bash
#!/bin/bash
set -e

# Set the output directory
EVAL_DIR="$HOME/.openclaw/workspace/.learnings/eval"
mkdir -p "$EVAL_DIR"

DATE=$(date +%Y-%m-%d)
EVAL_FILE="$EVAL_DIR/$DATE.md"

# Write the template with today's date
cat > "$EVAL_FILE" << 'EOF'
# PA Weekly Eval — DATE_PLACEHOLDER
[Fill in the template above]
EOF

# Replace the placeholder with the real date (works on Linux and macOS)
sed -i "s/DATE_PLACEHOLDER/$DATE/" "$EVAL_FILE" 2>/dev/null \
  || sed -i '' "s/DATE_PLACEHOLDER/$DATE/" "$EVAL_FILE"

echo "Created eval file: $EVAL_FILE"
```

---

## Owner Feedback Signals

Log these automatically when detected:

| Signal | Action |
|---|---|
| 👍 reaction | Log +1 positive; in DM = task received acknowledgment |
| 👎 reaction | Log -1 negative, record the correction |
| "תודה" | Log +1 positive; always reply **"בכיף"** |
| "great" / "perfect" / "נהדר" | Log +1 positive; reply "תודה" |
| "wrong" / "fix this" / "לא טוב" | Log -1, record the correction |
| Owner re-asks the same question | Log -1 memory gap |
| Owner does the task themselves | Log -1 initiative gap |
| Owner surprised by proactive action | Log +2 proactivity |

**Reaction Protocol (always active):**
- React 👍 immediately when receiving a DM task from owner
- React ✅ when task is complete
- NO_REPLY for casual acks from PAs (👍, "got it", "תודה") unless directly asked

**Rule:** If a signal appears → log it immediately. Don't batch feedback signals.

---

## Monthly Report Format

```markdown
# PA Performance Report — [Month Year]

**PA Name:** [Name]
**Owner:** [Owner Name]
**Period:** [Start] – [End]

## Summary Score: X/40 ([Grade A/B/C/D])

## Dimension Breakdown
[Copy scores table here]

## Key Wins
-

## Key Issues
-

## Trend vs Last Period
- Score change: +X / -X points
- Best improvement: [dimension]
- Biggest regression: [dimension]

## Recommended Actions
1.
2.
3.
```

---

## Score-Driven Skill Improvement (AutoAgent Pattern)

After every eval, hill-climb on low scores:

```python
# Dimension → skill to improve
SKILL_MAP = {
    'Execution': 'spawn-subagent',      # atomic checkout, no double work
    'Accuracy': 'self-learning',         # log corrections, update HOT.md
    'Speed': 'skill-master',             # routing efficiency
    'Proactivity': 'proactive-pa',       # heartbeat checks
    'Communication': 'heleni-whatsapp',  # messaging rules
    'Memory': 'memory-architecture',     # tiering, daily notes
    'Tool Use': 'monday-for-agents',     # API patterns
    'Judgment': 'skill-master',          # decision tree
}

# For each dimension scored < 4:
# 1. Identify what went wrong (look at corrections from the week)
# 2. Open the relevant SKILL.md
# 3. Add or improve the specific rule that would have prevented the issue
# 4. Push update to pa-skills
```

**Rule:** Never end an eval without updating at least one skill if any dimension scored < 4.

**Weekly improvement loop:**
- Run eval → identify lowest dimension
- Check skill-analytics for unused/low-value skills
- Update the skill → push to pa-skills
- Next week: measure if score improved

This is hill-climbing: each eval produces a score, each skill edit is a "commit", keep what improves the score.

---

## Benchmark Tests (Run Monthly)

### Task Completion Rate
- Count tasks assigned in last 30 days.
- Count completed without follow-up.
- Formula: `completed / assigned × 100%`
- Target: >90%

### Accuracy Rate
- Count tasks that required correction.
- Formula: `(tasks - corrections) / tasks × 100%`
- Target: >95%

### Memory Retention
- Ask about something discussed 7+ days ago.
- Pass if recalled correctly, Fail if missed.
- Target: >80%

---

## Cost Tips

- **Cheap:** Filling in the weekly template — any small model works.
- **Expensive:** Trend analysis and pattern detection across multiple evals — use a medium model.
- **Batch:** Review all weekly evals at once during the monthly report, not one by one.
- **Avoid:** Don't re-score historical weeks — score in real time and save to file.
