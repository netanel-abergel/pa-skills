#!/usr/bin/env python3
"""
auto_improve.py — Automated self-improvement loop.

Daily: scan eval_tracker corrections, detect recurring patterns, stage candidates.
Weekly: cross-reference candidates, draft rules, output proposals for owner approval.

Usage:
  python3 tools/auto_improve.py daily    # silent daily scan
  python3 tools/auto_improve.py weekly   # weekly report with rule proposals
  python3 tools/auto_improve.py status   # show current candidates
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict
from pathlib import Path

WORKSPACE = os.environ.get("WORKSPACE", "/path/to/openclaw/workspace")
EVAL_FILE = os.path.join(WORKSPACE, "data/eval_metrics.jsonl")
CANDIDATES_FILE = os.path.join(WORKSPACE, "data/improvement_candidates.jsonl")
RULES_LOG = os.path.join(WORKSPACE, "data/auto_rules.jsonl")


def load_eval_events(days=1):
    """Load eval events from the last N days."""
    if not os.path.exists(EVAL_FILE):
        return []
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    events = []
    
    with open(EVAL_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                ts = ev.get("timestamp", ev.get("ts", ""))
                if ts:
                    evt_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if evt_time.tzinfo is None:
                        evt_time = evt_time.replace(tzinfo=timezone.utc)
                    if evt_time >= cutoff:
                        events.append(ev)
                else:
                    events.append(ev)  # no timestamp, include
            except (json.JSONDecodeError, ValueError):
                continue
    
    return events


def load_candidates():
    """Load existing improvement candidates."""
    if not os.path.exists(CANDIDATES_FILE):
        return []
    
    candidates = []
    with open(CANDIDATES_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                candidates.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return candidates


def save_candidate(candidate):
    """Append a candidate to the candidates file."""
    os.makedirs(os.path.dirname(CANDIDATES_FILE), exist_ok=True)
    with open(CANDIDATES_FILE, "a") as f:
        f.write(json.dumps(candidate, ensure_ascii=False) + "\n")


def save_rule(rule):
    """Append an approved/proposed rule to the rules log."""
    os.makedirs(os.path.dirname(RULES_LOG), exist_ok=True)
    with open(RULES_LOG, "a") as f:
        f.write(json.dumps(rule, ensure_ascii=False) + "\n")


def daily_scan():
    """
    Daily silent scan:
    - Load corrections from last 24h
    - Detect patterns (same category/keyword appearing 2+ times)
    - Stage as candidates
    """
    events = load_eval_events(days=1)
    corrections = [e for e in events if e.get("type") == "correction"]
    
    if not corrections:
        print("No corrections in last 24h.")
        return
    
    # Group by category/description patterns
    categories = Counter()
    details = defaultdict(list)
    
    for c in corrections:
        desc = c.get("detail", c.get("description", c.get("message", "unknown")))
        # Extract category: first few meaningful words
        cat = _categorize(desc)
        categories[cat] += 1
        details[cat].append({
            "description": desc,
            "timestamp": c.get("timestamp", c.get("ts", "")),
            "context": c.get("context", "")
        })
    
    # Flag patterns appearing 2+ times in one day
    new_candidates = 0
    existing = load_candidates()
    existing_cats = {c.get("category", "") for c in existing if c.get("status") != "resolved"}
    
    for cat, count in categories.items():
        if count >= 2 and cat not in existing_cats:
            candidate = {
                "category": cat,
                "daily_count": count,
                "weekly_count": count,
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat(),
                "examples": details[cat][:5],
                "status": "staged",
                "proposed_rule": None
            }
            save_candidate(candidate)
            new_candidates += 1
            print(f"  New pattern: '{cat}' ({count}x today)")
        elif count >= 2 and cat in existing_cats:
            # Update existing candidate count
            print(f"  Recurring pattern: '{cat}' ({count}x today, already tracked)")
    
    print(f"\nDaily scan: {len(corrections)} corrections, {new_candidates} new candidates staged.")


def weekly_report(days=7, threshold=3):
    """
    Weekly analysis:
    - Cross-reference all candidates from the week
    - Patterns appearing 3+ times total → draft a rule
    - Output proposals for owner approval
    """
    # Load all corrections from last 7 days
    events = load_eval_events(days=days)
    corrections = [e for e in events if e.get("type") == "correction"]
    
    # Also load task failures
    failures = [e for e in events if e.get("type") == "task_failed"]
    
    # Group corrections
    categories = Counter()
    details = defaultdict(list)
    
    for c in corrections:
        desc = c.get("detail", c.get("description", c.get("message", "unknown")))
        cat = _categorize(desc)
        categories[cat] += 1
        details[cat].append(desc)
    
    # Load candidates and merge counts
    candidates = load_candidates()
    
    print("=" * 60)

    label = "DAILY" if days <= 1 else "WEEKLY"
    print(f"{label} SELF-IMPROVEMENT REPORT")
    print(f"Period: {(datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')} to {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    print(f"Total corrections: {len(corrections)}")
    print(f"Total failures: {len(failures)}")
    print("=" * 60)
    
    proposals = []
    
    # Patterns with 3+ occurrences → rule proposals
    for cat, count in categories.most_common(10):
        if count >= threshold:
            rule = _draft_rule(cat, details[cat])
            proposals.append({
                "category": cat,
                "occurrences": count,
                "proposed_rule": rule,
                "examples": details[cat][:3],
                "timestamp": datetime.utcnow().isoformat(),
                "status": "proposed"
            })
            save_rule({
                "category": cat,
                "occurrences": count,
                "proposed_rule": rule,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "proposed"
            })
            
            print(f"\n🔴 PATTERN: '{cat}' — {count} occurrences")
            print(f"   Proposed rule: {rule}")
            print(f"   Examples: {'; '.join(details[cat][:3])}")
    
    # Patterns with 2 occurrences → watch list
    watch = [(cat, count) for cat, count in categories.most_common() if count == 2]
    if watch:
        print(f"\n🟡 WATCH LIST ({len(watch)} patterns with 2 occurrences):")
        for cat, count in watch:
            print(f"   - {cat}")
    
    # Single corrections — info only
    singles = sum(1 for _, c in categories.items() if c == 1)
    if singles:
        print(f"\n⚪ {singles} one-off corrections (no pattern yet)")
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"PROPOSALS FOR APPROVAL: {len(proposals)}")
    for i, p in enumerate(proposals, 1):
        print(f"  {i}. [{p['category']}] → {p['proposed_rule']}")
    print("=" * 60)
    
    if not proposals:
        print("\nNo recurring patterns detected this week. All good.")
    
    return proposals


def status():
    """Show current candidates and their status."""
    candidates = load_candidates()
    
    if not candidates:
        print("No improvement candidates tracked.")
        return
    
    print(f"Improvement candidates: {len(candidates)}")
    for c in candidates:
        status_icon = {"staged": "🟡", "proposed": "🔵", "approved": "🟢", "resolved": "✅"}.get(c.get("status", ""), "⚪")
        print(f"  {status_icon} [{c.get('category', '?')}] count={c.get('weekly_count', '?')} status={c.get('status', '?')}")
        if c.get("proposed_rule"):
            print(f"     → Rule: {c['proposed_rule']}")


def _categorize(description):
    """Extract a rough category from a correction description."""
    if not description or description == "unknown":
        return "uncategorized"
    desc = description.lower().strip()
    
    # Known category patterns
    patterns = {
        "thinking_leak": ["thinking", "reasoning", "internal", "i need to", "let me check", "i should"],
        "format_error": ["format", "table", "header", "markdown", "bold"],
        "wrong_recipient": ["wrong", "recipient", "sent to", "wrong person"],
        "missing_context": ["context", "didn't check", "missed", "forgot"],
        "language_mix": ["hebrew", "english", "language", "mixed"],
        "too_long": ["too long", "verbose", "shorten", "shorter"],
        "too_short": ["too short", "missing detail", "incomplete"],
        "wrong_tone": ["tone", "formal", "casual", "professional"],
        "duplicate": ["duplicate", "already said", "repeated"],
        "permission_violation": ["permission", "approval", "unauthorized"],
        "stale_data": ["stale", "outdated", "old data", "not current"],
    }
    
    for cat, keywords in patterns.items():
        if any(kw in desc for kw in keywords):
            return cat
    
    # Fallback: first 3 meaningful words
    words = [w for w in desc.split()[:5] if len(w) > 3]
    return "_".join(words[:3]) if words else "uncategorized"


def _draft_rule(category, examples):
    """Draft a rule based on the category and examples."""
    rule_templates = {
        "thinking_leak": "HARD BLOCK: Strip any sentence describing internal process before sending. Enforce via thinking-filter plugin.",
        "format_error": "Before sending to WhatsApp: verify no markdown tables/headers. Bold and bullets only.",
        "wrong_recipient": "MANDATORY: Verify recipient phone/JID in contact-list.md before every send.",
        "missing_context": "Before replying: run memory_search + DB query. Never say 'no context' without checking all layers.",
        "language_mix": "Match language to recipient preference. Owner DM: per USER.md preference. Groups: per group language.",
        "too_long": "Apply smart-output compression. WhatsApp ≤800 chars. Cut lowest-scored items first.",
        "too_short": "Ensure response addresses all parts of the question. Re-read before sending.",
        "wrong_tone": "Match tone to context: owner=casual, groups=professional, PAs=direct.",
        "duplicate": "Run dedup_check before every send. Never repeat content from the same thread.",
        "permission_violation": "Irreversible actions require explicit owner approval. No exceptions.",
        "stale_data": "For mutable facts (files, git, services): always live-check before stating.",
    }
    
    if category in rule_templates:
        return rule_templates[category]
    
    return f"Recurring issue in '{category}'. Review examples and codify prevention rule. Examples: {'; '.join(examples[:2])}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: auto_improve.py [daily|weekly|status]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "daily":
        daily_scan()
    elif cmd == "weekly":
        weekly_report()
    elif cmd == "daily-report":
        # Combined: scan today + report with 2+ threshold (more aggressive than weekly)
        daily_scan()
        print("\n")
        weekly_report(days=1, threshold=2)
    elif cmd == "status":
        status()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
