#!/usr/bin/env python3
"""Commitment Checker — reads commitments.jsonl, finds PENDING items,
flags STALE ones (>7 days), and outputs actionable recommendations.

Usage:
  python3 tools/check_commitments.py
"""
import json
import sys
from datetime import datetime, timezone, timedelta

LOG = "/path/to/workspace/data/commitments.jsonl"
STALE_DAYS = 7


def load_commitments():
    """Load all commitments from JSONL."""
    items = []
    try:
        with open(LOG) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print("No commitments.jsonl found.")
        sys.exit(0)
    return items


def parse_date(item):
    """Extract creation date from various field names."""
    for field in ["created_at", "created", "ts"]:
        if field in item:
            try:
                return datetime.fromisoformat(
                    item[field].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                continue
    return None


def main():
    items = load_commitments()
    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=STALE_DAYS)

    # Filter to pending only (case-insensitive)
    pending = [
        i for i in items
        if str(i.get("status", "")).upper() == "PENDING"
    ]

    done = [
        i for i in items
        if str(i.get("status", "")).lower() == "done"
    ]

    if not pending:
        print(f"All clear. {len(done)} commitments done, 0 pending.")
        sys.exit(0)

    print(f"=== Commitment Check ===")
    print(f"Total: {len(items)} | Done: {len(done)} | Pending: {len(pending)}")
    print()

    stale_items = []
    active_items = []

    for item in pending:
        created = parse_date(item)
        item_id = item.get("id", item.get("action", "unknown"))
        desc = item.get("description", item.get("note", item.get("action", "")))
        owner = item.get("owner", "heleni")
        target = item.get("target", "")

        age_days = (now - created).days if created else None
        is_stale = age_days is not None and age_days > STALE_DAYS

        entry = {
            "id": item_id,
            "desc": desc,
            "owner": owner,
            "target": target,
            "age_days": age_days,
            "is_stale": is_stale,
            "created": created.strftime("%Y-%m-%d") if created else "unknown",
            "raw": item,
        }

        if is_stale:
            stale_items.append(entry)
        else:
            active_items.append(entry)

    # Report stale items first (higher priority)
    if stale_items:
        print(f"🔴 STALE ({len(stale_items)} items older than {STALE_DAYS} days):")
        for e in stale_items:
            print(f"  [{e['id']}] {e['desc'][:80]}")
            print(f"    Age: {e['age_days']}d | Owner: {e['owner']} | Created: {e['created']}")
            # Generate actionable recommendation
            if e["owner"] == "heleni":
                if e["target"]:
                    print(f"    → ACTION: Execute now — send to {e['target']}")
                else:
                    print(f"    → ACTION: Execute now or mark as done/cancelled")
            else:
                print(f"    → ACTION: Ask owner ({e['owner']}) — still needed?")
            print()

    # Report active items
    if active_items:
        print(f"🟡 ACTIVE ({len(active_items)} pending items):")
        for e in active_items:
            print(f"  [{e['id']}] {e['desc'][:80]}")
            print(f"    Age: {e['age_days']}d | Owner: {e['owner']} | Created: {e['created']}")
            if e["owner"] == "heleni":
                due = e["raw"].get("due", e["raw"].get("remind_at", ""))
                if due:
                    print(f"    → ACTION: Execute by {due}")
                else:
                    print(f"    → ACTION: Execute when ready")
            else:
                print(f"    → ACTION: Monitor — owned by {e['owner']}")
            print()

    # Summary
    print(f"Summary: {len(stale_items)} stale, {len(active_items)} active")
    if stale_items:
        sys.exit(1)  # Non-zero = needs attention


if __name__ == "__main__":
    main()
