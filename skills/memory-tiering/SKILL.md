---
name: memory-tiering
description: Automated multi-tiered memory management (HOT, WARM, COLD). Use this skill to organize, prune, and archive context during memory operations or compactions.
---

# Memory Tiering Skill 🧠⚖️

> **2026.4.10 Update:** OpenClaw now has two native memory systems — **Active Memory** (runs before every reply) and **Dreaming** (nightly consolidation at 3 AM IL). This skill covers what they DON'T handle — see section below.

## What Native Systems Now Cover (don't duplicate)

| Task | Who does it |
|---|---|
| Pull relevant context before each reply | Active Memory plugin (automatic) |
| Promote strong signals to MEMORY.md nightly | Dreaming / memory-core (automatic) |
| HOT.md pattern promotion after 2x mistakes | self-learning skill |

## What This Skill Still Handles

- Manual pruning when MEMORY.md grows >200 lines
- Archiving old `memory/daily/YYYY-MM-DD.md` files (30-day retention)
- Force-promoting critical owner corrections immediately (don't wait for Dreaming)
- Reviewing DREAMS.md after first 2 weeks to validate promotion quality
- Post-compaction reorganization
- Enforcing store boundaries: daily notes = raw-first log, `MEMORY.md` = durable rules only, project docs = project-scoped

## The Three Tiers (for manual ops)

1.  **🔥 HOT (`memory/hot/HOT_MEMORY.md`)** — current session, active tasks
2.  **🌡️ WARM (`memory/warm/WARM_MEMORY.md`)** — stable preferences, configs
3.  **❄️ COLD (`MEMORY.md`)** — long-term, distilled, curated

## Workflow: `Organize-Memory` (Manual / Post-Compaction)

### Step 1: Check native systems first
```bash
openclaw memory status --deep   # see what Dreaming already promoted
/dreaming status                  # check last run
```

### Step 2: Ingest & Audit
- Read MEMORY.md + last 7 `memory/daily/YYYY-MM-DD.md` files
- Identify Dead Context: completed tasks, resolved issues, stale facts

### Step 3: Prune & Redistribute
- Remove stale COLD entries (if Dreaming already promoted better versions)
- Force-add critical owner corrections → MEMORY.md immediately (don't wait for Dreaming)
- Archive daily notes older than 30 days → `memory/archive/YYYY-MM/`

### Step 4: Verify
- MEMORY.md should be <200 lines after cleanup
- Check `DREAMS.md` — are Dreaming's promotions accurate? Prune bad ones.

## Usage Trigger
- Trigger manually: "Run memory tiering" or when MEMORY.md >200 lines
- Trigger automatically after any `/compact` command

---

## Dreaming Integration (OpenClaw 2026.4.9+)

Dreaming is **already enabled** (`memory-core` plugin, `0 3 * * *` IL timezone).

**What Dreaming does automatically:**
- Light phase: ingests daily notes + session transcripts
- Deep phase: scores & promotes strong signals → MEMORY.md (weighted: relevance 0.30, frequency 0.24, recency 0.15)
- REM phase: extracts themes and patterns

**Manual CLI for inspection/intervention:**
```bash
openclaw memory status --deep          # what's queued for promotion
openclaw memory promote                # preview what would promote
openclaw memory promote --apply        # force apply now
openclaw memory promote-explain "term" # why something would/wouldn't promote
/dreaming status                        # last run summary
```

**What still requires manual action:**
- Owner corrections → MEMORY.md **immediately** (don't wait for Dreaming)
- Critical session-startup rules → MEMORY.md **manually**
- Pruning bad/stale Dreaming promotions → manual cleanup
- MEMORY.md growing >200 lines → prune manually

### Safety Rules
- Content changes (MEMORY.md): require explicit review — never auto-apply
- Archiving old files: safe to run automatically
- `trash` > `rm` always

### Retention Policy
- Daily notes: keep 30 days → archive to `memory/archive/YYYY-MM/`
- Archive: keep 90 days → delete
- MEMORY.md: prune if >200 lines

### Health Indicators
- ✅ Healthy: MEMORY.md <200 lines, DREAMS.md updated nightly, daily notes exist
- ⚠️ Warning: MEMORY.md 200–300 lines, Dreaming didn't run in 48h
- ❌ Critical: MEMORY.md >300 lines, no Dreaming output in 7 days
