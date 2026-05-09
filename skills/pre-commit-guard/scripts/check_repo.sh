#!/usr/bin/env bash
# Pre-commit checks for heleni-memory.
set -e
fail=0

# 1. Credential scan
if git diff --cached --name-only | xargs -I{} grep -l -E 'eyJ[A-Za-z0-9_\-]{20,}\.eyJ|gh[ps]_[A-Za-z0-9]{36}|xox[bp]-[0-9-]+-[A-Za-z0-9]+' {} 2>/dev/null; then
    echo "❌ credential pattern detected in staged files — abort"
    fail=1
fi

# 2. SKILL.md frontmatter
for f in $(git diff --cached --name-only | grep -E 'skills/.*/SKILL\.md$'); do
    if ! head -10 "$f" | grep -q '^name:'; then
        echo "❌ $f missing 'name:' in frontmatter"; fail=1
    fi
    if ! head -10 "$f" | grep -q '^description:'; then
        echo "❌ $f missing 'description:' in frontmatter"; fail=1
    fi
done

# 3. Oversized doctrine files
for f in *.md; do
    [ -f "$f" ] || continue
    size=$(wc -c < "$f")
    if [ "$size" -gt 102400 ]; then
        echo "⚠ $f is $((size/1024))KB — consider trimming or moving to memory/"
    fi
done

# 4. Doctrine integrity — block if any commit deletes >50% of a doctrine file
# Background: HOT.md rule #15 — Heleni once silently rewrote SOUL.md during a "cleanup"
# commit, losing 17 sections of behavioral doctrine. This check prevents recurrence.
DOCTRINE_FILES="SOUL.md IDENTITY.md USER.md AGENTS.md HOT.md"
for f in $DOCTRINE_FILES; do
    [ -f "$f" ] || continue
    # Skip if file is not staged for modification
    git diff --cached --name-only | grep -q "^${f}$" || continue
    # Get current size and proposed (staged) size
    current_lines=$(wc -l < "$f")
    staged_lines=$(git show ":${f}" 2>/dev/null | wc -l)
    if [ "$current_lines" -gt 0 ] && [ "$staged_lines" -lt $((current_lines / 2)) ]; then
        echo "❌ $f: staged version is $staged_lines lines vs current $current_lines (>50% deletion). Doctrine rewrite requires explicit owner approval — abort"
        fail=1
    fi
done

exit $fail
