# smart-output

## Purpose
Self-reflection, compression, and chain-of-thought refinement on structured outputs before delivery.
Inspired by PR-Agent's core abilities — adapted for general PA use beyond code review.

## When to activate
- Any structured output with multiple items (briefings, lists, recommendations, action items)
- Long-form content before sending (LinkedIn posts, reports, summaries)
- Memory compaction passes (daily note → MEMORY.md promotion candidates)
- Multi-step tasks where intermediate output feeds the next stage

## Do NOT activate
- Simple direct answers (one-liner replies)
- Heartbeat checks
- System ops (cron, gateway, git)
- When speed matters more than quality (urgent alerts)

## Pipeline

### Stage 1: Generate
Produce the raw output as normal. No filtering yet.

### Stage 2: Self-Reflect (score + filter)
Review every item in the output. For each:
- Score 0-10 on relevance, accuracy, and value to the recipient
- Flag items scoring 0 as incorrect/irrelevant — remove them
- Flag items scoring 1-3 as low-value — remove unless nothing else remains
- Re-rank remaining items by score (descending)

Decision rule:
- If generating ≤3 items: skip scoring, just sanity-check each
- If generating 4+ items: full score-and-filter pass
- Threshold: configurable, default = 4 (drop items below this score)

### Stage 3: Compress (token-aware fitting)
When output exceeds the delivery medium's practical limit:
- WhatsApp: ~800 chars ideal, 1500 max
- LinkedIn: ~1300 chars for posts, ~300 for comments
- Briefing DM: ~500 chars
- Internal/file: no hard limit, but prefer concise

Compression strategy:
1. Prioritize additions/new info over restated context
2. Sort items by score (from Stage 2)
3. Fit highest-scored items first until limit approached
4. Remaining items: collapse to one-line mentions ("Also: X, Y, Z")
5. If still over: drop lowest-scored items entirely

### Stage 4: Chain (multi-stage metadata injection)
When a task has multiple stages:
1. Stage N produces a structured summary
2. Stage N+1 receives that summary as injected context (not raw output)
3. Each stage builds on the refined output of the previous one

Examples:
- Meeting notes → action item extraction → priority ranking → owner assignment
- Daily notes → theme extraction → MEMORY.md candidate scoring → promotion
- Content draft → self-review → revision → format for platform

No extra API calls — all stages run within the same session turn.

## Asymmetric Context Rule
When retrieving context for any recall or analysis task:
- Pull MORE context from BEFORE the event/change (history, setup, motivation)
- Pull LESS context from AFTER (results, follow-ups)
- Prefer enclosing context (the project, the thread, the conversation) over isolated snippets

Ratio guideline: ~3:1 before:after when context budget is limited.

## Configuration
```yaml
smart_output:
  self_reflect: true
  score_threshold: 4          # drop items below this
  min_items_for_scoring: 4    # skip scoring for tiny outputs
  compress: true
  chain: true
  asymmetric_context: true
  context_ratio: 3            # before:after ratio
```

## Anti-patterns
- Do NOT self-reflect on self-reflection output (no recursion)
- Do NOT compress when the user explicitly asked for "everything" or "full list"
- Do NOT chain more than 3 stages without intermediate output review
- Do NOT apply to real-time/urgent sends (alerts, permission requests)

## Interaction with other skills
- **memory-tiering**: Stage 2 scoring aligns with graduation gate criteria (score ≥ 0.70, recalls ≥ 2)
- **eval**: Self-reflection results feed eval_tracker silently (log quality improvements)
- **proactive-pa**: Proactive surface candidates go through Stage 2 before delivery
- **owner-briefing**: Morning briefing items go through full pipeline (generate → score → compress → send)
