#!/usr/bin/env python3
"""
Heleni Eval Tracker — Quantitative self-evaluation metrics.

Tracks:
- Owner corrections (negative signal)
- Positive feedback (thumbs up, thanks, etc.)
- Task completion rate
- Memory recall accuracy
- Proactive actions taken

Stores everything in a JSONL file for trend analysis.
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

IL_TZ = timezone(timedelta(hours=3))
DATA_DIR = "/opt/ocana/openclaw/workspace/data"
EVAL_FILE = os.path.join(DATA_DIR, "eval_metrics.jsonl")
WEEKLY_DIR = "/opt/ocana/openclaw/workspace/memory/eval"


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(WEEKLY_DIR, exist_ok=True)


def log_event(event_type: str, detail: str = "", score: int = 0):
    """Log a single eval event."""
    ensure_dirs()
    entry = {
        "ts": datetime.now(IL_TZ).isoformat(),
        "type": event_type,
        "detail": detail,
        "score": score,
    }
    with open(EVAL_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Logged: {event_type} ({score:+d})")


def load_events(days: int = 7) -> list:
    """Load events from the last N days."""
    if not os.path.exists(EVAL_FILE):
        return []
    cutoff = datetime.now(IL_TZ) - timedelta(days=days)
    events = []
    with open(EVAL_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry["ts"])
                if ts >= cutoff:
                    events.append(entry)
            except (json.JSONDecodeError, KeyError):
                continue
    return events


def weekly_report():
    """Generate a weekly quantitative report."""
    events = load_events(days=7)
    if not events:
        print("No eval data in the last 7 days.")
        return

    # Count by type
    counts = {}
    total_score = 0
    for e in events:
        t = e["type"]
        counts[t] = counts.get(t, 0) + 1
        total_score += e.get("score", 0)

    corrections = counts.get("correction", 0)
    positive = counts.get("positive_feedback", 0)
    tasks_done = counts.get("task_completed", 0)
    tasks_failed = counts.get("task_failed", 0)
    proactive = counts.get("proactive_action", 0)
    memory_hit = counts.get("memory_hit", 0)
    memory_miss = counts.get("memory_miss", 0)

    total_tasks = tasks_done + tasks_failed
    task_rate = (tasks_done / total_tasks * 100) if total_tasks > 0 else 0
    total_memory = memory_hit + memory_miss
    memory_rate = (memory_hit / total_memory * 100) if total_memory > 0 else 0

    report = {
        "period": f"{(datetime.now(IL_TZ) - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now(IL_TZ).strftime('%Y-%m-%d')}",
        "total_events": len(events),
        "net_score": total_score,
        "corrections": corrections,
        "positive_feedback": positive,
        "feedback_ratio": f"{positive}:{corrections}",
        "tasks_completed": tasks_done,
        "tasks_failed": tasks_failed,
        "task_completion_rate": f"{task_rate:.0f}%",
        "proactive_actions": proactive,
        "memory_hits": memory_hit,
        "memory_misses": memory_miss,
        "memory_accuracy": f"{memory_rate:.0f}%",
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))

    # Save to weekly file
    ensure_dirs()
    week_file = os.path.join(
        WEEKLY_DIR, f"{datetime.now(IL_TZ).strftime('%Y-%m-%d')}-weekly.json"
    )
    with open(week_file, "w") as f:
        json.dumps(report, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {week_file}")
    return report


def trend_report():
    """Compare last 4 weekly reports for trends."""
    ensure_dirs()
    files = sorted(
        [f for f in os.listdir(WEEKLY_DIR) if f.endswith("-weekly.json")]
    )[-4:]

    if len(files) < 2:
        print("Need at least 2 weekly reports for trend analysis.")
        return

    reports = []
    for fname in files:
        with open(os.path.join(WEEKLY_DIR, fname)) as f:
            reports.append(json.loads(f.read()))

    print("=== TREND REPORT ===")
    for r in reports:
        print(
            f"{r['period']}: score={r['net_score']:+d} | "
            f"tasks={r['task_completion_rate']} | "
            f"memory={r['memory_accuracy']} | "
            f"corrections={r['corrections']} | "
            f"proactive={r['proactive_actions']}"
        )


def usage():
    print(
        """Usage: eval_tracker.py <command> [args]

Commands:
  log <type> [detail] [score]   Log an event
    Types: correction, positive_feedback, task_completed, task_failed,
           proactive_action, memory_hit, memory_miss, failure_rule_added
    Score: numeric, default based on type

  weekly                        Generate weekly report
  trend                         Compare last 4 weeks
  raw [days]                    Dump raw events (default 7 days)

Examples:
  eval_tracker.py log correction "sent to wrong group" -2
  eval_tracker.py log positive_feedback "owner said great" 1
  eval_tracker.py log task_completed "calendar setup" 1
  eval_tracker.py log proactive_action "flagged billing issue" 2
  eval_tracker.py weekly
"""
    )


# Commitment trigger words
COMMITMENT_TRIGGERS_HE = [r'\bי?אשלח\b', r'\bי?אדווח\b', r'\bי?אעדכן\b', r'\bי?אוסיף\b', r'\bי?אחזור\b', r'\bי?אבדוק\b', r'\bי?אעביר\b']
COMMITMENT_TRIGGERS_EN = [r"i'?ll send", r"i'?ll report", r"i'?ll update", r"i'?ll follow", r"i'?ll check", r"i'?ll let you know", r"i'?ll message", r"i'?ll notify"]
NO_CONTEXT_PHRASES = ['אין לי context', 'I don\'t have context', 'I don\'t remember', 'אני לא זוכרת', 'לא מוכר לי']

def check_reply(text):
    """Analyze a reply for commitment triggers, no-context phrases, etc."""
    import re
    warnings = []
    
    # Check commitments
    for pat in COMMITMENT_TRIGGERS_HE + COMMITMENT_TRIGGERS_EN:
        if re.search(pat, text, re.IGNORECASE):
            warnings.append(f"COMMITMENT: matches '{pat}'")
    
    # Check no-context without search evidence
    for phrase in NO_CONTEXT_PHRASES:
        if phrase.lower() in text.lower():
            warnings.append(f"MEMORY_MISS: says '{phrase}' — was search done?")
    
    if warnings:
        for w in warnings:
            event_type = 'memory_miss' if 'MEMORY_MISS' in w else 'commitment_detected'
            log_event(event_type, w, -1 if 'MEMORY_MISS' in w else 0)
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠️  {w}")
    else:
        print("PASS — no issues detected")
    return warnings


# Default scores by type
DEFAULT_SCORES = {
    "correction": -1,
    "positive_feedback": 1,
    "task_completed": 1,
    "task_failed": -1,
    "proactive_action": 2,
    "memory_hit": 1,
    "memory_miss": -1,
    "failure_rule_added": 1,
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "log":
        if len(sys.argv) < 3:
            print("Error: need event type")
            sys.exit(1)
        event_type = sys.argv[2]
        detail = sys.argv[3] if len(sys.argv) > 3 else ""
        score = int(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_SCORES.get(
            event_type, 0
        )
        log_event(event_type, detail, score)

    elif cmd == "weekly":
        weekly_report()

    elif cmd == "trend":
        trend_report()

    elif cmd == "raw":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        events = load_events(days)
        for e in events:
            print(json.dumps(e, ensure_ascii=False))
        print(f"\nTotal: {len(events)} events in last {days} days")

    elif cmd == "check-reply":
        if len(sys.argv) < 3:
            print("Error: need message text")
            sys.exit(1)
        check_reply(sys.argv[2])

    else:
        usage()
        sys.exit(1)
