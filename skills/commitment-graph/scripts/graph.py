#!/usr/bin/env python3
"""Commitment graph viewer — overdue, chains, repeat offenders."""
import argparse
import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Optional

COMMITMENTS_FILE = Path("data/commitments.jsonl")


def load() -> List[dict]:
    if not COMMITMENTS_FILE.exists():
        return []
    return [json.loads(line) for line in COMMITMENTS_FILE.read_text().splitlines() if line.strip()]


def overdue(items: List[dict], today: Optional[date] = None) -> List[dict]:
    today = today or date.today()
    out = []
    for it in items:
        if it.get("status") == "done":
            continue
        due = it.get("due_date")
        if not due:
            continue
        try:
            d = datetime.fromisoformat(due).date()
        except ValueError:
            continue
        if d < today:
            it["age_days"] = (today - d).days
            out.append(it)
    return sorted(out, key=lambda x: x["age_days"], reverse=True)


def repeat_offenders(items: List[dict], threshold: int = 3) -> Dict[str, int]:
    counts: defaultdict = defaultdict(int)
    od = overdue(items)
    for it in od:
        counts[it.get("committed_by", "?")] += 1
    return {k: v for k, v in counts.items() if v >= threshold}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--overdue", action="store_true")
    p.add_argument("--offenders", action="store_true")
    args = p.parse_args()

    items = load()
    if args.overdue or not (args.overdue or args.offenders):
        for it in overdue(items):
            print(f"  [{it['age_days']}d overdue] {it.get('committed_by','?')} → {it.get('action','?')} (for {it.get('requester','?')})")
    if args.offenders:
        for who, n in repeat_offenders(items).items():
            print(f"  REPEAT OFFENDER: {who} ({n} overdue)")


if __name__ == "__main__":
    main()
