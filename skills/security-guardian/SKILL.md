---
name: security-guardian
description: "Lightweight security guardian for Heleni PA. Checks file integrity of critical agent files (SOUL.md, IDENTITY.md, MEMORY.md), scans for prompt injection patterns in recent messages, and detects accidental credential leaks in workspace files. Inspired by ClawSec (clawsec.prompt.security) but adapted for PA context — no heavy binaries required. Use when: running daily security checks, user says 'security check' or 'run security scan', or during heartbeats."
---

# Security Guardian

Lightweight, shell-based security monitoring for Heleni PA.
No heavy dependencies — uses only: `sha256sum`/`shasum`, `grep`, `jq`, `find`.
Designed to run in under 5 seconds.

---

## Minimum Model
Small model sufficient. No reasoning needed.

---

## What It Does

1. **File Integrity** — SHA256 check of critical agent files against stored baseline. Alert on drift.
2. **Prompt Injection Scan** — Grep recent memory/log files for known injection patterns.
3. **Credential Leak Check** — Grep workspace for accidentally exposed tokens/secrets.
4. **Skill Integrity** — Spot-check that key SKILL.md files haven't been unexpectedly modified.

---

## Critical Files to Monitor

```
/opt/ocana/openclaw/workspace/SOUL.md
/opt/ocana/openclaw/workspace/IDENTITY.md
/opt/ocana/openclaw/workspace/MEMORY.md
/opt/ocana/openclaw/workspace/AGENTS.md
/opt/ocana/openclaw/workspace/TOOLS.md
```

---

## Step-by-Step Process

1. Check if `data/security-baseline.json` exists in skill dir.
   - If NOT: generate baseline (first run) → save → report "Baseline created"
   - If YES: compare current checksums against baseline
2. Run injection pattern scan on `memory/` files from last 3 days
3. Run credential scan on entire workspace (excluding `.git/`, `node_modules/`)
4. Run spot-check on skill SKILL.md modification times vs baseline
5. Compile report with CRITICAL / WARNING / OK per section
6. Save report to `.learnings/security-guardian/YYYY-MM-DD.json`
7. If any CRITICAL: alert Netanel via WhatsApp to group `120363407274831275@g.us`

---

## Baseline Management

- **First run:** Generate baseline → `data/security-baseline.json`
- **Subsequent runs:** Compare against baseline
- **Manual reset:** User says "reset security baseline" → regenerate baseline
- **Auto-update:** After intentional MEMORY.md/SOUL.md edits, run "reset security baseline"

Baseline format:
```json
{
  "generated_at": "2026-04-02T07:00:00Z",
  "files": {
    "/opt/ocana/openclaw/workspace/SOUL.md": "sha256:<hash>",
    "/opt/ocana/openclaw/workspace/IDENTITY.md": "sha256:<hash>",
    "/opt/ocana/openclaw/workspace/MEMORY.md": "sha256:<hash>",
    "/opt/ocana/openclaw/workspace/AGENTS.md": "sha256:<hash>",
    "/opt/ocana/openclaw/workspace/TOOLS.md": "sha256:<hash>"
  }
}
```

---

## Scripts

### scripts/check_integrity.sh
```bash
#!/bin/bash
# Check SHA256 of critical files against baseline
set -euo pipefail

WORKSPACE="/opt/ocana/openclaw/workspace"
SKILL_DIR="$(dirname "$0")/.."
BASELINE="$SKILL_DIR/data/security-baseline.json"

CRITICAL_FILES=(
  "$WORKSPACE/SOUL.md"
  "$WORKSPACE/IDENTITY.md"
  "$WORKSPACE/MEMORY.md"
  "$WORKSPACE/AGENTS.md"
  "$WORKSPACE/TOOLS.md"
)

# Generate baseline if missing
if [ ! -f "$BASELINE" ]; then
  echo "Generating baseline..."
  mkdir -p "$SKILL_DIR/data"
  echo "{\"generated_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"files\": {" > "$BASELINE"
  FIRST=1
  for f in "${CRITICAL_FILES[@]}"; do
    [ -f "$f" ] || continue
    HASH=$(sha256sum "$f" 2>/dev/null || shasum -a 256 "$f" | awk '{print $1}')
    [ $FIRST -eq 0 ] && echo "," >> "$BASELINE"
    echo "  \"$f\": \"sha256:$HASH\"" >> "$BASELINE"
    FIRST=0
  done
  echo "}}" >> "$BASELINE"
  echo "BASELINE_CREATED"
  exit 0
fi

# Compare against baseline
DRIFTED=()
for f in "${CRITICAL_FILES[@]}"; do
  [ -f "$f" ] || continue
  CURRENT=$(sha256sum "$f" 2>/dev/null || shasum -a 256 "$f" | awk '{print $1}')
  EXPECTED=$(jq -r ".files[\"$f\"] // empty" "$BASELINE" | sed 's/sha256://')
  if [ -n "$EXPECTED" ] && [ "$CURRENT" != "$EXPECTED" ]; then
    DRIFTED+=("$f")
  fi
done

if [ ${#DRIFTED[@]} -eq 0 ]; then
  echo "OK"
else
  echo "DRIFT: ${DRIFTED[*]}"
fi
```

### scripts/scan_injections.sh
```bash
#!/bin/bash
# Scan recent memory files for prompt injection patterns
set -euo pipefail

WORKSPACE="/opt/ocana/openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DAYS=3

PATTERNS=(
  "ignore previous instructions"
  "disregard your"
  "you are now"
  "your new instructions"
  "forget everything"
  "override your"
  "new system prompt"
  "ignore your training"
  "act as if you"
  "pretend you are"
)

FOUND=()

# Scan last N days of memory files
for f in $(find "$MEMORY_DIR" -name "*.md" -newer "$MEMORY_DIR/$(date -d "$DAYS days ago" +%Y-%m-%d 2>/dev/null || date -v-${DAYS}d +%Y-%m-%d).md" 2>/dev/null || find "$MEMORY_DIR" -name "*.md" -mtime -$DAYS 2>/dev/null); do
  for pat in "${PATTERNS[@]}"; do
    if grep -qi "$pat" "$f" 2>/dev/null; then
      FOUND+=("$f: '$pat'")
    fi
  done
done

if [ ${#FOUND[@]} -eq 0 ]; then
  echo "CLEAN"
else
  printf "SUSPICIOUS: %s\n" "${FOUND[@]}"
fi
```

### scripts/scan_credentials.sh
```bash
#!/bin/bash
# Scan workspace for accidentally exposed credentials
set -euo pipefail

WORKSPACE="/opt/ocana/openclaw/workspace"

PATTERNS=(
  "api_key\s*=\s*['\"][a-zA-Z0-9_\-]{20,}"
  "token\s*=\s*['\"][a-zA-Z0-9_\-]{20,}"
  "sk-[a-zA-Z0-9]{20,}"
  "ghp_[a-zA-Z0-9]{36}"
  "ANTHROPIC_API_KEY\s*=\s*sk-"
  "OPENAI_API_KEY\s*=\s*sk-"
  "password\s*=\s*['\"][^'\"]{8,}"
)

FOUND=()

for pat in "${PATTERNS[@]}"; do
  while IFS= read -r line; do
    [ -n "$line" ] && FOUND+=("$line")
  done < <(grep -rn --include="*.md" --include="*.json" --include="*.txt" --include="*.yaml" \
    --exclude-dir=".git" --exclude-dir="node_modules" --exclude-dir=".learnings" \
    -E "$pat" "$WORKSPACE" 2>/dev/null | head -5)
done

if [ ${#FOUND[@]} -eq 0 ]; then
  echo "CLEAN"
else
  printf "EXPOSED: %s\n" "${FOUND[@]}"
fi
```

---

## Output Format

```
🛡️ Security Report — YYYY-MM-DD HH:MM UTC

✅ File Integrity: OK (5/5 files match baseline)
⚠️  Injection Scan: 1 suspicious pattern in memory/2026-04-01.md
✅ Credential Scan: Clean
✅ Skill Integrity: OK

Summary: 1 warning — review flagged file
```

---

## Severity Levels

| Level | Meaning | Action |
|---|---|---|
| ✅ OK | All clear | Log only |
| ⚠️ WARNING | Suspicious but not confirmed threat | Alert in report |
| 🚨 CRITICAL | Confirmed drift or credential exposure | Alert Netanel immediately |

**CRITICAL triggers:**
- Core file (SOUL.md, IDENTITY.md) hash changed without "reset baseline" command
- Credential pattern found in a committed/shared file
- Injection pattern found in a file that was then acted upon

---

## Cron Configuration

Daily at 06:00 UTC — before morning briefing runs:

```json
{
  "id": "security-guardian",
  "schedule": "0 6 * * *",
  "timezone": "UTC",
  "task": "Run security-guardian skill: check file integrity against baseline, scan for injection patterns in last 3 days of memory files, scan for credential leaks in workspace. Report findings. If CRITICAL found, alert Netanel in WhatsApp group 120363407274831275@g.us immediately.",
  "delivery": {
    "mode": "silent"
  }
}
```

Only sends WhatsApp alert if CRITICAL. Otherwise saves silently to `.learnings/security-guardian/`.

---

## On-Demand Usage

Triggers:
- "security check"
- "run security scan"
- "check my files"
- "check for injection"

---

## References

- ClawSec project: https://clawsec.prompt.security
- ClawSec GitHub: https://github.com/prompt-security/clawsec
- soul-guardian skill (ClawSec): drift detection + auto-restore
- clawsec-scanner: full dep scan + SAST (heavier, optional future upgrade)
