---
name: spec-lite
description: "Lightweight task contract for non-trivial work. Use when a request will take more than 10-15 minutes, has multiple steps, affects external delivery, or needs an explicit definition of done. Turns a vague ask into a mini spec: goal, constraints, acceptance criteria, verification, and done gate."
---

# Spec Lite

Use this skill before starting non-trivial work.

## When to Use

Trigger for work that is:
- More than 10-15 minutes
- Multi-step or cross-file
- User-visible or externally delivered
- Easy to mark done too early
- Risky to execute without explicit checks

Do not use for tiny asks like:
- one-line answers
- simple lookups
- obvious one-file edits
- routine acknowledgements

## Output Contract

Before execution, write a mini spec in 5 parts.

### 1. Goal
What exactly should exist or be true when the task is complete?

### 2. Constraints
What must be preserved or avoided?
Examples:
- no personal data exposure
- no downtime
- no schema change
- no user-facing emoji

### 3. Acceptance Criteria
List 3-7 concrete checks.
Use observable language.

Good:
- morning briefing arrives at 07:00 Asia/Jerusalem
- public repo contains SKILL.md only, no `.context`
- message is in English and has no table

Bad:
- works well
- looks good
- should be fine

### 4. Verification
How will you prove each criterion?
Examples:
- read the file
- run the script
- inspect the diff
- verify recipient / timezone / target
- confirm output shape

### 5. Done Gate
The task is not done until:
- all acceptance criteria pass
- risky outputs were verified
- obvious follow-up was handled
- status reported honestly

## Execution Pattern

1. Extract the request into the 5-part mini spec.
2. Execute.
3. Verify against the acceptance criteria.
4. Only then report done.

## Default Mini Spec Template

```md
## Spec Lite
- Goal:
- Constraints:
- Acceptance Criteria:
  -
  -
  -
- Verification:
  -
  -
  -
- Done Gate:
  - all criteria checked
```

## Recommended Checks by Task Type

### Messaging
- right recipient
- right timing
- right language/style
- no duplicated send
- no private data leak

### Cron / automation
- exact schedule
- timezone
- target channel / recipient
- payload matches requested output
- no stale old schedule left behind

### Skill / repo changes
- SKILL.md stays generic
- no `.context`, `data/`, secrets, or private references
- trigger description is clear
- instructions are concise
- public version matches local intent

### Meeting prep / briefing
- calendar matches today
- overlaps called out explicitly
- prep bullets are tied to real context
- output is short enough to use live

## Rule of Thumb

If the risk of a false "done" is meaningful, use Spec Lite.
