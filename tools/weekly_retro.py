#!/usr/bin/env python3
"""Weekly Retro Generator — produces a structured retrospective markdown.

Sources:
  - git log (last 7 days)
  - .learnings/ entries from the week
  - memory/daily/ notes
  - Previous week's retro for comparison

Output: memory/retros/YYYY-WXX.md

Usage:
  python3 tools/weekly_retro.py           # generate and save
  python3 tools/weekly_retro.py --dry-run # preview without saving
"""
import argparse
import os
import re
import subprocess
import sys
import sys as _sys
# Prevent tools/calendar.py from shadowing stdlib calendar
_tools_dir = os.path.dirname(os.path.abspath(__file__))
if _tools_dir in _sys.path:
    _sys.path.remove(_tools_dir)
from datetime import datetime, timezone, timedelta

WORKSPACE = "/path/to/openclaw/workspace"
RETRO_DIR = os.path.join(WORKSPACE, "memory/retros")
DAILY_DIR = os.path.join(WORKSPACE, "memory/daily")
LEARNINGS_FILE = os.path.join(WORKSPACE, ".learnings/LEARNINGS.md")


def get_week_info():
    """Return current ISO week info."""
    now = datetime.now(timezone.utc)
    iso = now.isocalendar()
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)
    return {
        "year": iso[0],
        "week": iso[1],
        "label": f"{iso[0]}-W{iso[1]:02d}",
        "start": week_start,
        "end": week_end,
        "start_str": week_start.strftime("%b %d"),
        "end_str": week_end.strftime("%b %d"),
    }


def get_git_log(days=7):
    """Get git log for the last N days."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "-C", WORKSPACE, "log", f"--since={since}",
             "--oneline", "--no-merges", "--format=%h %s"],
            capture_output=True, text=True, timeout=10
        )
        commits = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
        return commits
    except Exception:
        return []


def get_git_stats(days=7):
    """Get git stats for the period."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "-C", WORKSPACE, "log", f"--since={since}",
             "--shortstat", "--no-merges"],
            capture_output=True, text=True, timeout=10
        )
        insertions = sum(int(m) for m in re.findall(r"(\d+) insertion", result.stdout))
        deletions = sum(int(m) for m in re.findall(r"(\d+) deletion", result.stdout))
        return {"insertions": insertions, "deletions": deletions}
    except Exception:
        return {"insertions": 0, "deletions": 0}


def get_daily_notes(week_start, week_end):
    """Read daily notes from the week."""
    notes = []
    if not os.path.isdir(DAILY_DIR):
        return notes
    for fname in sorted(os.listdir(DAILY_DIR)):
        if not fname.endswith(".md"):
            continue
        date_str = fname.replace(".md", "")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if week_start.date() <= date.date() <= week_end.date():
                with open(os.path.join(DAILY_DIR, fname)) as f:
                    content = f.read()
                notes.append({"date": date_str, "content": content})
        except ValueError:
            continue
    return notes


def get_week_learnings(week_start, week_end):
    """Extract learnings logged during the week."""
    if not os.path.exists(LEARNINGS_FILE):
        return []

    with open(LEARNINGS_FILE) as f:
        content = f.read()

    learnings = []
    blocks = re.split(r"(?=^## \[)", content, flags=re.MULTILINE)
    for block in blocks:
        if not block.startswith("## ["):
            continue

        logged_match = re.search(r"\*\*Logged\*\*:\s*([\d\-T:Z]+)", block)
        date_match = re.match(r"## \[([\d]{4}-[\d]{2}-[\d]{2})\]", block)

        logged_date = None
        if logged_match:
            try:
                logged_date = datetime.fromisoformat(
                    logged_match.group(1).replace("Z", "+00:00")
                )
            except ValueError:
                pass
        elif date_match:
            try:
                logged_date = datetime.fromisoformat(date_match.group(1) + "T00:00:00+00:00")
            except ValueError:
                pass

        if logged_date and week_start.date() <= logged_date.date() <= week_end.date():
            summary_match = re.search(r"### Summary\n(.+)", block)
            status_match = re.search(r"\*\*Status\*\*:\s*(\w+)", block)
            cat_match = re.search(r"## \[[\w-]+\]\s*(\w+)", block)

            summary = summary_match.group(1).strip() if summary_match else block.split("\n")[0]
            status = status_match.group(1) if status_match else "unknown"
            category = cat_match.group(1) if cat_match else ""

            learnings.append({
                "summary": summary,
                "status": status,
                "category": category,
                "date": logged_date.strftime("%Y-%m-%d"),
            })

    return learnings


def get_previous_retro(week_label):
    """Try to load previous week's retro for comparison."""
    # Parse current week and compute previous
    match = re.match(r"(\d{4})-W(\d{2})", week_label)
    if not match:
        return None
    year, week = int(match.group(1)), int(match.group(2))
    prev_week = week - 1
    prev_year = year
    if prev_week < 1:
        prev_year -= 1
        prev_week = 52

    prev_label = f"{prev_year}-W{prev_week:02d}"
    prev_file = os.path.join(RETRO_DIR, f"{prev_label}.md")
    if os.path.exists(prev_file):
        with open(prev_file) as f:
            return {"label": prev_label, "content": f.read()}
    return None


def extract_themes_from_dailies(notes):
    """Extract key themes from daily notes."""
    themes = {"shipped": [], "blockers": [], "people": set()}
    for note in notes:
        for line in note["content"].split("\n"):
            line_stripped = line.strip().lower()
            if any(w in line_stripped for w in ["shipped", "completed", "done", "deployed", "launched"]):
                themes["shipped"].append(line.strip())
            if any(w in line_stripped for w in ["blocked", "stuck", "failed", "error", "bug"]):
                themes["blockers"].append(line.strip())
    return themes


def generate_retro(dry_run=False):
    """Generate the weekly retro."""
    week = get_week_info()
    commits = get_git_log()
    stats = get_git_stats()
    notes = get_daily_notes(week["start"], week["end"])
    learnings = get_week_learnings(week["start"], week["end"])
    prev_retro = get_previous_retro(week["label"])
    themes = extract_themes_from_dailies(notes)

    # Categorize commits
    commit_categories = {"fix": [], "feat": [], "refactor": [], "docs": [], "other": []}
    for c in commits:
        c_lower = c.lower()
        if any(w in c_lower for w in ["fix", "patch", "hotfix", "bug"]):
            commit_categories["fix"].append(c)
        elif any(w in c_lower for w in ["feat", "add", "new", "create", "implement"]):
            commit_categories["feat"].append(c)
        elif any(w in c_lower for w in ["refactor", "cleanup", "simplify", "optimize"]):
            commit_categories["refactor"].append(c)
        elif any(w in c_lower for w in ["doc", "readme", "comment", "note"]):
            commit_categories["docs"].append(c)
        else:
            commit_categories["other"].append(c)

    # Build retro markdown
    md = []
    md.append(f"# Weekly Retro — {week['label']} ({week['start_str']}–{week['end_str']})")
    md.append("")

    # Summary section
    md.append("## Summary")
    md.append(f"Commits: {len(commits)} | Learnings: {len(learnings)} | Daily notes: {len(notes)}")
    md.append(f"Lines: +{stats['insertions']} / -{stats['deletions']}")
    md.append("")

    # Shipped
    md.append("## Shipped")
    if commit_categories["feat"]:
        for c in commit_categories["feat"][:10]:
            md.append(f"- {c}")
    else:
        md.append("- (no feature commits detected)")
    md.append("")

    # Fixes
    md.append("## Fixes")
    if commit_categories["fix"]:
        for c in commit_categories["fix"][:10]:
            md.append(f"- {c}")
    else:
        md.append("- (no fix commits detected)")
    md.append("")

    # Learnings
    md.append("## Learnings")
    if learnings:
        applied = [l for l in learnings if l["status"] == "applied"]
        pending = [l for l in learnings if l["status"] == "pending"]
        md.append(f"Applied: {len(applied)} | Pending: {len(pending)}")
        for l in learnings:
            status_icon = "✅" if l["status"] == "applied" else "⏳"
            md.append(f"- {status_icon} [{l['date']}] {l['summary'][:80]}")
    else:
        md.append("- No learnings logged this week")
    md.append("")

    # Patterns
    md.append("## Patterns")
    if themes["blockers"]:
        md.append("### Blockers seen")
        for b in themes["blockers"][:5]:
            md.append(f"- {b[:100]}")
    else:
        md.append("- No recurring blockers detected")
    md.append("")

    # Comparison with previous week
    md.append("## Week-over-Week")
    if prev_retro:
        md.append(f"Previous: {prev_retro['label']}")
        # Try to extract commit count from previous retro
        prev_commits_match = re.search(r"Commits:?\s*(\d+)", prev_retro["content"])
        if prev_commits_match:
            prev_count = int(prev_commits_match.group(1))
            delta = len(commits) - prev_count
            direction = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            md.append(f"Commit delta: {direction} {abs(delta)}")
    else:
        md.append("No previous retro available for comparison.")
    md.append("")

    # Priorities for next week
    md.append("## Priorities for Next Week")
    pending_learnings = [l for l in learnings if l["status"] == "pending"]
    if pending_learnings:
        md.append("Based on pending learnings:")
        for l in pending_learnings[:5]:
            md.append(f"- Apply: {l['summary'][:60]}")
    else:
        md.append("- (review daily notes and set priorities)")
    md.append("")

    retro_text = "\n".join(md)

    if dry_run:
        print("=== DRY RUN — would save to: ===")
        outfile = os.path.join(RETRO_DIR, f"{week['label']}.md")
        print(f"File: {outfile}")
        print()
        print(retro_text)
        return

    # Save
    os.makedirs(RETRO_DIR, exist_ok=True)
    outfile = os.path.join(RETRO_DIR, f"{week['label']}.md")
    with open(outfile, "w") as f:
        f.write(retro_text)
    print(f"Retro saved to {outfile}")
    print(retro_text)


def main():
    parser = argparse.ArgumentParser(description="Weekly Retro Generator")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    args = parser.parse_args()
    generate_retro(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
