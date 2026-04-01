---
name: pa-eval
description: "Evaluate PA performance through structured scoring, owner feedback analysis, and behavioral benchmarking. Use when: conducting a weekly/monthly PA performance review, owner gives feedback (positive or negative), assessing response quality, or identifying areas for improvement."
---

# PA Eval Skill

Structured performance evaluation for AI Personal Assistants.

---

## Evaluation Dimensions

Score each dimension 1–5:

| Dimension | What to Measure |
|---|---|
| **Execution** | Does the PA complete tasks without being reminded? |
| **Accuracy** | Are results correct, complete, and verified? |
| **Speed** | How quickly does the PA respond and execute? |
| **Proactivity** | Does the PA anticipate needs and act without being asked? |
| **Communication** | Is output concise, clear, and appropriate to context? |
| **Memory** | Does the PA remember context across sessions? |
| **Tool Use** | Does the PA use available tools correctly and efficiently? |
| **Judgment** | Does the PA know when to act vs. when to ask? |

---

## Scoring Rubric

| Score | Meaning |
|---|---|
| 5 | Excellent — consistently exceeds expectations |
| 4 | Good — meets expectations with minor gaps |
| 3 | Acceptable — meets basic expectations |
| 2 | Needs improvement — frequent gaps or errors |
| 1 | Poor — fails to meet basic expectations |

---

## Weekly Self-Evaluation

Run this weekly. Save output to `.learnings/eval/YYYY-MM-DD.md`.

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

---

## Owner Feedback Signals

Log and score these automatically:

| Signal | Impact |
|---|---|
| 👍 reaction | +1 positive signal |
| 👎 reaction | -1 negative signal, log correction |
| "תודה" / "great" / "perfect" | +1 positive |
| "לא טוב" / "wrong" / "fix this" | -1 negative, log correction |
| Repeated question (owner re-asks same thing) | -1 memory gap |
| Owner does task themselves instead of delegating | -1 initiative gap |
| Owner expresses surprise at proactive action | +2 proactivity |

---

## Benchmark Tests

Run monthly to measure capability:

### Task Completion Rate
- Count tasks assigned in last 30 days
- Count tasks completed without follow-up
- Rate = completed / assigned × 100%
- Target: >90%

### Response Time
- Measure time from message received to first action
- Target: <30 seconds for simple tasks, <2 min for complex

### Accuracy Rate
- Count tasks where output required correction
- Rate = (tasks - corrections) / tasks × 100%
- Target: >95%

### Memory Retention
- Ask about something discussed 7+ days ago
- Score: recalled correctly (pass) / missed (fail)
- Target: >80% retention of important facts

---

## Evaluation Report Format

```markdown
# PA Performance Report — [Month] [Year]

**PA Name:** [Name]
**Owner:** [Owner Name]
**Evaluation Period:** [Start] – [End]

## Summary Score: X/40 ([Grade])

A (36–40) | B (28–35) | C (20–27) | D (<20)

## Dimension Breakdown
[Scores table]

## Key Wins
- 

## Key Issues
- 

## Trend vs Last Period
- Score: +X / -X points
- Best improvement: [dimension]
- Biggest regression: [dimension]

## Recommended Actions
1. 
2. 
3. 
```

---

## Storing Eval Data

```bash
#!/bin/bash
set -e

EVAL_DIR="$HOME/.openclaw/workspace/.learnings/eval"
mkdir -p "$EVAL_DIR"
DATE=$(date +%Y-%m-%d)
EVAL_FILE="$EVAL_DIR/$DATE.md"

# Save eval (replace [eval content] with actual content)
cat > "$EVAL_FILE" << 'EOF'
[eval content]
EOF

echo "Saved to $EVAL_FILE"

# View history
echo "Eval history:"
ls "$EVAL_DIR/"
```

---

## Model Compatibility

This skill works with any LLM model that can follow structured templates.

| Task | Minimum Model |
|---|---|
| Filling in the weekly eval template | Any |
| Scoring dimensions from memory | Small–Medium |
| Pattern analysis across multiple evals | Medium model recommended |
| Generating trend analysis and recommendations | Medium–Large |

No provider-specific APIs are used. Eval data is stored as plain markdown files — readable and editable by any LLM or human.
