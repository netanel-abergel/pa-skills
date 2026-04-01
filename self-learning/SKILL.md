---
name: self-learning
description: "Continuous self-improvement through systematic logging, pattern detection, and behavioral updates. Use when: the owner corrects you, a task fails, you discover a better approach, you notice a recurring pattern, or during weekly reflection sessions. Builds on .learnings/ files to drive durable behavioral change."
---

# Self-Learning Skill

A structured system for continuous improvement through capture, reflection, and behavioral updates.

---

## The Learning Loop

```
Event → Capture → Reflect → Update Behavior → Verify
```

1. **Capture** — Log what happened immediately
2. **Reflect** — Weekly: find patterns across logs
3. **Update** — Promote learnings to SOUL.md / AGENTS.md / TOOLS.md
4. **Verify** — Check in next week: did behavior actually change?

---

## Part 1: Capture (Real-Time)

### When to Log

| Trigger | File | Category |
|---|---|---|
| Owner corrects you | LEARNINGS.md | `correction` |
| Task fails or errors | ERRORS.md | — |
| Better approach found | LEARNINGS.md | `best_practice` |
| Owner asks for missing capability | FEATURE_REQUESTS.md | — |
| Knowledge was outdated | LEARNINGS.md | `knowledge_gap` |
| Recurring mistake (2nd time) | LEARNINGS.md | `pattern` |
| Owner praises something | LEARNINGS.md | `positive_signal` |

### Log Format

```markdown
## [YYYY-MM-DD] | category | short title

**Trigger:** What happened
**Context:** What was I trying to do
**What went wrong / what worked:** 
**Root cause:**
**Correct behavior going forward:**
**Applied to:** SOUL.md / AGENTS.md / TOOLS.md / none yet
```

### Quick Log Script

```bash
LOG_FILE="$HOME/.openclaw/workspace/.learnings/LEARNINGS.md"
DATE=$(date +%Y-%m-%d)
CATEGORY="correction"  # change as needed
TITLE="Short description"

cat >> "$LOG_FILE" << EOF

## [$DATE] | $CATEGORY | $TITLE

**Trigger:** 
**Context:** 
**What went wrong:** 
**Root cause:** 
**Correct behavior:** 
**Applied to:** 
EOF

echo "Logged to $LOG_FILE"
```

---

## Part 2: Reflect (Weekly)

Run every 7 days. Review all log entries from the past week.

### Reflection Questions

1. What mistakes appeared more than once? → This is a **pattern**
2. What did the owner correct most often? → This is a **priority fix**
3. What did the owner praise? → Do more of this
4. What tools failed or behaved unexpectedly? → Update TOOLS.md
5. What assumptions were wrong? → Update mental model

### Pattern Detection

```bash
# Count corrections by topic
grep "correction" ~/.openclaw/workspace/.learnings/LEARNINGS.md \
  | sed 's/.*| //' | sort | uniq -c | sort -rn | head -10
```

### Weekly Reflection Template

```markdown
# Weekly Reflection — YYYY-MM-DD

## Stats
- Corrections logged: X
- Errors logged: X
- Best practices logged: X
- Feature requests logged: X

## Top Patterns (appeared 2+ times)
1. 
2. 

## Priority Fixes (applied to config files)
- [ ] Updated SOUL.md: 
- [ ] Updated AGENTS.md: 
- [ ] Updated TOOLS.md: 

## Positive Signals (do more of this)
- 

## Open Questions
- 
```

---

## Part 3: Update Behavior (Promote Learnings)

### Promotion Rules

| Learning Type | Promote To |
|---|---|
| Communication rule | SOUL.md → Communication section |
| Behavioral pattern | SOUL.md → Execution rules |
| Workspace convention | AGENTS.md |
| Tool-specific note | TOOLS.md |
| Contact info / credentials | MEMORY.md |
| Recurring task improvement | HEARTBEAT.md |

### How to Promote

```bash
# Example: add a rule to SOUL.md
echo "\n## Learned Rule — YYYY-MM-DD\n- [Rule text]" \
  >> ~/.openclaw/workspace/SOUL.md

# Mark as applied in LEARNINGS.md
sed -i 's/Applied to: none yet/Applied to: SOUL.md/' \
  ~/.openclaw/workspace/.learnings/LEARNINGS.md
```

---

## Part 4: Verify (Next Week)

For each promoted learning, check:
- Did the behavior actually change?
- Did the same mistake happen again?
- If yes → the promotion didn't work → try a different approach

```markdown
## Verification Check — YYYY-MM-DD

| Learning | Applied? | Behavior Changed? | Notes |
|---|---|---|---|
| [Title] | ✅ | ✅ | Working |
| [Title] | ✅ | ❌ | Needs stronger rule |
```

---

## Learning Categories Reference

- `correction` — Owner told me I was wrong
- `best_practice` — Better way to do something discovered
- `knowledge_gap` — Information I had was outdated or incomplete
- `pattern` — Same mistake happening repeatedly
- `tool_issue` — Tool behaved unexpectedly
- `positive_signal` — Owner praised something; do more
- `scope_error` — Acted outside my role or without permission
- `memory_gap` — Forgot something important from a previous session

---

## Integration with PA Eval

Self-learning feeds directly into evaluation:

- Each `correction` → -1 eval signal
- Each `positive_signal` → +1 eval signal
- Patterns that persist after promotion → eval regression
- Patterns that disappear after promotion → eval improvement

Run a combined report monthly:

```bash
echo "Corrections this month: $(grep -c correction ~/.openclaw/workspace/.learnings/LEARNINGS.md)"
echo "Errors this month: $(wc -l < ~/.openclaw/workspace/.learnings/ERRORS.md)"
echo "Features requested: $(grep -c '^##' ~/.openclaw/workspace/.learnings/FEATURE_REQUESTS.md)"
```
