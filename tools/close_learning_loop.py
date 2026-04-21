#!/usr/bin/env python3
"""Learning-to-Skill Closer — scans LEARNINGS.md for pending entries that
should be promoted into skill updates.

Flags entries where:
  - Status is "pending" AND recurrence-count >= 2
  - Status is "pending" AND pending > 14 days

For each flagged entry: identifies which skill should be updated and outputs
a recommended action.
"""
import re
import sys
from datetime import datetime, timezone, timedelta

LEARNINGS_FILE = "/opt/ocana/openclaw/workspace/.learnings/LEARNINGS.md"

# Map tags/areas to skills
TAG_TO_SKILL = {
    "communication": "heleni-whatsapp",
    "whatsapp": "heleni-whatsapp",
    "heartbeat": "proactive-pa",
    "cron": "proactive-pa",
    "memory": "memory-tiering",
    "recall": "memory-tiering",
    "pa-onboarding": "pa-onboarding",
    "pa-coordination": "pa-onboarding",
    "config": "pa-maintenance",
    "billing": "billing-monitor",
    "eval": "eval",
    "identity": "pa-maintenance",
    "security": "pa-maintenance",
    "operations": "pa-maintenance",
    "docs": "memory-tiering",
    "self-improvement": "self-learning",
    "context": "heleni-whatsapp",
    "dm": "heleni-whatsapp",
    "groups": "heleni-whatsapp",
    "dedup": "heleni-whatsapp",
    "monday": "pa-onboarding",
    "troubleshooting": "pa-onboarding",
}


def parse_learnings(filepath: str) -> list[dict]:
    """Parse LEARNINGS.md into structured entries."""
    with open(filepath) as f:
        content = f.read()

    entries = []
    # Split on ## [LRN- or ## [2026- headings
    blocks = re.split(r"(?=^## \[)", content, flags=re.MULTILINE)

    for block in blocks:
        block = block.strip()
        if not block.startswith("## ["):
            continue

        entry = {"raw_header": block.split("\n")[0]}

        # Extract ID
        id_match = re.match(r"## \[(LRN-[\w-]+|[\d-]+)\]", block)
        entry["id"] = id_match.group(1) if id_match else "unknown"

        # Extract status
        status_match = re.search(r"\*\*Status\*\*:\s*(\w+)", block)
        entry["status"] = status_match.group(1).lower() if status_match else "unknown"

        # Extract logged date
        logged_match = re.search(r"\*\*Logged\*\*:\s*([\d\-T:Z]+)", block)
        if logged_match:
            try:
                entry["logged"] = datetime.fromisoformat(
                    logged_match.group(1).replace("Z", "+00:00")
                )
            except ValueError:
                entry["logged"] = None
        else:
            # Try date from ID like [2026-04-16]
            date_match = re.match(r"## \[([\d]{4}-[\d]{2}-[\d]{2})\]", block)
            if date_match:
                entry["logged"] = datetime.fromisoformat(
                    date_match.group(1) + "T00:00:00+00:00"
                )
            else:
                entry["logged"] = None

        # Extract recurrence count
        rec_match = re.search(r"Recurrence-Count:\s*(\d+)", block)
        entry["recurrence"] = int(rec_match.group(1)) if rec_match else 0

        # Extract tags
        tags_match = re.search(r"Tags:\s*(.+)", block)
        entry["tags"] = (
            [t.strip() for t in tags_match.group(1).split(",")]
            if tags_match
            else []
        )

        # Extract summary
        summary_match = re.search(r"### Summary\n(.+)", block)
        if not summary_match:
            # Fallback: use the header line after category
            hdr = block.split("\n")[0]
            pipe_parts = hdr.split("|")
            entry["summary"] = pipe_parts[-1].strip() if len(pipe_parts) > 1 else hdr
        else:
            entry["summary"] = summary_match.group(1).strip()

        # Extract area
        area_match = re.search(r"\*\*Area\*\*:\s*(\w+)", block)
        entry["area"] = area_match.group(1).lower() if area_match else ""

        # Extract applied-to
        applied_match = re.findall(r"Applied to:\s*(.+)", block)
        entry["applied_to"] = applied_match

        entries.append(entry)

    return entries


def identify_skill(entry: dict) -> str:
    """Best-guess which skill should be updated based on tags/area."""
    for tag in entry.get("tags", []):
        tag_lower = tag.lower().strip()
        if tag_lower in TAG_TO_SKILL:
            return TAG_TO_SKILL[tag_lower]
    area = entry.get("area", "")
    if area in TAG_TO_SKILL:
        return TAG_TO_SKILL[area]
    return "SOUL.md / HOT.md (general)"


def main():
    now = datetime.now(timezone.utc)
    cutoff_14d = now - timedelta(days=14)

    try:
        entries = parse_learnings(LEARNINGS_FILE)
    except FileNotFoundError:
        print("No LEARNINGS.md found.")
        sys.exit(0)

    pending = [e for e in entries if e["status"] == "pending"]

    if not pending:
        print("No pending learnings found. All clear.")
        sys.exit(0)

    flagged = []
    for e in pending:
        reasons = []
        if e["recurrence"] >= 2:
            reasons.append(f"recurrence={e['recurrence']} (>=2, pattern confirmed)")
        if e["logged"] and e["logged"] < cutoff_14d:
            age = (now - e["logged"]).days
            reasons.append(f"pending for {age} days (>14, stale)")
        if reasons:
            e["flag_reasons"] = reasons
            flagged.append(e)

    print(f"=== Learning Loop Closer ===")
    print(f"Total learnings: {len(entries)}")
    print(f"Pending: {len(pending)}")
    print(f"Flagged for action: {len(flagged)}")
    print()

    if not flagged:
        print("No pending learnings need promotion yet.")
        # Still list pending for awareness
        for e in pending:
            age = (now - e["logged"]).days if e["logged"] else "?"
            print(f"  [{e['id']}] {e['summary'][:60]}... (age={age}d, rec={e['recurrence']})")
        sys.exit(0)

    for e in flagged:
        skill = identify_skill(e)
        print(f"--- {e['id']} ---")
        print(f"  Summary: {e['summary'][:80]}")
        print(f"  Reasons: {', '.join(e['flag_reasons'])}")
        print(f"  Tags: {', '.join(e['tags'])}")
        print(f"  Target skill: {skill}")
        if e.get("applied_to"):
            print(f"  Already applied to: {'; '.join(e['applied_to'])}")
            print(f"  ACTION: Mark as 'applied' in LEARNINGS.md (already implemented)")
        else:
            print(f"  ACTION: Update skill '{skill}' with this learning, then mark as 'applied'")
        print()


if __name__ == "__main__":
    main()
