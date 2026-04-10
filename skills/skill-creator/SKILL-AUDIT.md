# Skill Audit Guide — When to Keep, Merge, or Move

A practical reference for cleaning up skill bloat. Sweet spot: 28–35 skills.
Above ~40, routing degrades — the agent picks wrong or picks nothing.

## 0. Red Flags — Audit Now If You See These

- Agent often picks the wrong skill (or none)
- Two skills answer the same scenario
- A skill exists only for troubleshooting/diagnostics
- A skill encodes always-on behavioral rules
- Setup always requires two skills together in the same session
- You have >40 skills

If any of these are true → work through the decision tree below.

---

## 1. Placement Decision Tree

For each skill, ask in order:

```
Does this rule apply to EVERY interaction?
  → YES → SOUL.md (not a skill)

Is this a core agent runtime capability?
  → YES → AGENTS.md (not a skill)

Is this only a troubleshooting/diagnostic appendix?
  → YES → Add as section in the parent skill, delete standalone

Do two skills share the same trigger or output?
  → YES → Merge (see rubric below)

Are two skills always used together in the same session?
  → YES → Merge into one

Otherwise → keep as standalone skill
```

---

## 2. Merge Rubric

Merge if ANY of these are true:

- Same trigger phrase routes to both
- Same output format (both generate a "report", "status", etc.)
- One skill calls the other >50% of the time
- You can't write one clean sentence explaining when to use A vs B
- They manage the same resource (memory files, calendar, etc.)

---

## 3. Five-Minute Overlap Test

Take the `description:` field from each skill's SKILL.md frontmatter.
Feed both to the agent: *"Which skill handles [scenario]?"*

If it hesitates, answers wrong, or gives both — they overlap. Merge.

---

## 4. Common Merge Patterns (with examples)

| Pattern | Example | Action |
|---|---|---|
| Same question, different scope | pa-status + supervisor | Merge: one skill, two sections |
| Diagnostics as standalone | whatsapp-diagnostics | Move to parent skill appendix |
| Always-on behavioral rule | dynamic-temperature | Move to SOUL.md |
| Core runtime capability | spawn-subagent | Move to AGENTS.md |
| Always used together | email-orientation + calendar-setup | Merge into one skill |
| Same resource, two skills | memory-maintenance + memory-tiering | Pick one, absorb the other |

---

## 5. Before / After Directory Example

**Before (40 skills — bloated):**
```
skills/
  pa-eval/
  eval/
  pa-status/
  supervisor/
  whatsapp/
  whatsapp-diagnostics/
  spawn-subagent/
  memory-tiering/
  memory-maintenance/
  dynamic-temperature/
  openclaw-email-orientation/
  calendar-setup/
```

**After (32 skills — clean):**
```
skills/
  eval/              ← absorbed pa-eval
  supervisor/        ← absorbed pa-status
  whatsapp/          ← absorbed whatsapp-diagnostics (as appendix)
  memory-tiering/    ← absorbed memory-maintenance
  calendar-setup/    ← absorbed openclaw-email-orientation
AGENTS.md            ← absorbed spawn-subagent
SOUL.md              ← absorbed dynamic-temperature
```

---

## 6. DEPRECATED.md Template

When you merge or move a skill, leave a `DEPRECATED.md` in the old folder.
Do NOT delete the folder — it preserves reasoning.

```markdown
# DEPRECATED — [skill-name]

**Status:** Merged into [destination]
**Date:** YYYY-MM-DD
**Reason:** [one sentence why]
**Lesson:** [the reusable rule]
**Moved to:** [destination] — Section "[section name]"
```

---

## 7. Key Rules

1. Skills are for triggered domain workflows — not universal behavior
2. Universal behavior → SOUL.md
3. Core runtime capabilities → AGENTS.md
4. Diagnostics → appendix in parent skill
5. If you can't explain A vs B in one sentence → merge
6. Always leave a DEPRECATED.md when retiring a skill
7. Target: 28–35 skills. If you hit 40+, audit immediately.
