---
name: self-monitor
version: 1.1.0
author: Polycat
tags: [monitoring, health, infrastructure]
license: MIT
platform: universal
description: >
  Proactive self-monitoring of infrastructure, services, and health. Tracks
  disk/memory/load, service health, cron job status, recent errors. Auto-fixes safe
  issues. Triggers on: health check, heartbeat, monitor status, service status,
  infrastructure check.
---

> **Compatible with Claude Code, Codex CLI, Cursor, Windsurf, and any SKILL.md-compatible agent.**

# Self Monitor

Proactive self-monitoring: infrastructure, services, and health.

## Usage

Run during heartbeats or scheduled checks.

### 1. Infrastructure Health

```bash
# Disk usage
df -h / | awk 'NR==2 {print $5}' | tr -d '%'

# Memory usage  
free -m | awk 'NR==2 {printf "%.0f", $3/$2*100}'

# Load average
uptime | awk -F'load average:' '{print $2}' | awk -F',' '{print $1}'

# Top processes by memory
ps aux --sort=-%mem | head -10

# Top processes by CPU
ps aux --sort=-%cpu | head -10
```

**Thresholds:**
| Metric | Warning | Critical |
|--------|---------|----------|
| Disk | > 80% | > 90% |
| Memory | > 85% | > 95% |
| Load | > 2.0 | > 4.0 |

### 2. Service Health

```bash
# Check if a process is running
pgrep -f "your_process_name" >/dev/null && echo "OK" || echo "FAIL"

# Check HTTP endpoint
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health

# Check systemd service
systemctl is-active --quiet nginx && echo "OK" || echo "FAIL"

# Check Docker container
docker ps --filter "name=mycontainer" --filter "status=running" -q | grep -q . && echo "OK" || echo "FAIL"

# Tailscale (if using)
tailscale status --json 2>/dev/null | jq -r '.Self.Online' || echo "FAIL"
```

### 3. Cron Job Health

```bash
# Check recent cron executions
grep CRON /var/log/syslog | tail -20

# Count failures in last 24h
grep -c "CRON.*error\|CRON.*fail" /var/log/syslog

# List scheduled jobs
crontab -l
```

### 4. Recent Errors

```bash
# Check system logs for errors
journalctl -p err --since "1 hour ago" 2>/dev/null | tail -20

# Check application logs
tail -50 ~/workspace/projects/*/logs/*.log 2>/dev/null | grep -i "error"

# Check dmesg for hardware/kernel issues
dmesg | tail -20 | grep -i "error\|fail\|warn"
```

## Quick Health Check (for heartbeat)

```bash
#!/bin/bash
# Quick health snapshot

DISK=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
MEM=$(free -m | awk 'NR==2 {printf "%.0f", $3/$2*100}')
LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk -F',' '{print $1}' | xargs)

echo "Disk: ${DISK}% | Mem: ${MEM}% | Load: ${LOAD}"

# Alert if thresholds exceeded
[ "$DISK" -gt 90 ] && echo "⚠️ Disk critical!"
[ "$MEM" -gt 95 ] && echo "⚠️ Memory critical!"
```

## Proactive Actions

**When issues detected:**

| Issue | Auto-Action | Alert? |
|-------|------------|--------|
| Disk > 90% | Clean temp files, old logs | Yes |
| Key process down | Attempt restart | Yes |
| Cron 3+ failures | Generate report | Yes |
| Memory > 95% | List top processes | Yes |

**Auto-fixable (safe):**
```bash
# Clean old logs (> 7 days)
find /var/log -name "*.log" -mtime +7 -delete 2>/dev/null
find ~/.cache -type f -mtime +7 -delete 2>/dev/null

# Clean temp files
rm -f /tmp/agent-temp-* 2>/dev/null
rm -rf ~/.cache/pip 2>/dev/null
```

## Report Format

```markdown
## 🔍 Self-Monitor Report - [TIME]

### Health Summary
| Metric | Value | Status |
|--------|-------|--------|
| Disk | XX% | ✅/⚠️/🔴 |
| Memory | XX% | ✅/⚠️/🔴 |
| Load | X.X | ✅/⚠️/🔴 |
| Services | X/Y up | ✅/⚠️ |

### Issues Found
- [Issue 1]: [Action taken or recommended]

### Top Resource Consumers
| Process | CPU% | MEM% |
|---------|------|------|
| ... | ... | ... |
```

## Integration with Scheduled Tasks

Add to your crontab or task scheduler:
```cron
# Run health check every 30 minutes
*/30 * * * * /path/to/health-check.sh >> /var/log/health-check.log 2>&1
```

Or run manually as part of your workflow:
```bash
./health-check.sh
```

---

## Security Checks

Run daily (or alongside any health check). Uses only `sha256sum`/`shasum`, `grep`, `find`, `jq`. Designed to complete in under 5 seconds.

### Critical Files to Monitor

```
/opt/ocana/openclaw/workspace/SOUL.md
/opt/ocana/openclaw/workspace/IDENTITY.md
/opt/ocana/openclaw/workspace/MEMORY.md
/opt/ocana/openclaw/workspace/AGENTS.md
/opt/ocana/openclaw/workspace/TOOLS.md
```

### 1. File Integrity (SHA256 Baseline)

See `../security-guardian/scripts/check_integrity.sh` for the full script.

Logic:
- On first run: generate `data/security-baseline.json` with SHA256 of each critical file
- On subsequent runs: compare current hashes against baseline; report any drift
- Manual reset: "reset security baseline" → regenerate baseline (do this after intentional edits to SOUL.md/MEMORY.md)

Baseline format:
```json
{
  "generated_at": "2026-04-02T07:00:00Z",
  "files": {
    "/opt/ocana/openclaw/workspace/SOUL.md": "sha256:<hash>"
  }
}
```

### 2. Prompt Injection Scan

See `../security-guardian/scripts/scan_injections.sh` for the full script.

Scans last 3 days of `memory/*.md` files for patterns like:
- "ignore previous instructions"
- "you are now" / "pretend you are"
- "forget everything" / "override your"
- "new system prompt"

### 3. Credential Leak Scan

See `../security-guardian/scripts/scan_credentials.sh` for the full script.

Scans workspace `*.md`, `*.json`, `*.txt`, `*.yaml` (excluding `.git/`, `node_modules/`) for:
- `api_key = 'xxx'` / `token = 'xxx'`
- `sk-...` (OpenAI/Anthropic keys)
- `ghp_...` (GitHub tokens)
- Hardcoded passwords

### Security Report Format

```
🛡️ Security Report — YYYY-MM-DD HH:MM UTC

✅ File Integrity: OK (5/5 files match baseline)
⚠️  Injection Scan: 1 suspicious pattern in memory/2026-04-01.md
✅ Credential Scan: Clean

 Summary: 1 warning — review flagged file
```

### Severity & Alerting

| Level | Meaning | Action |
|---|---|---|
| ✅ OK | All clear | Log only |
| ⚠️ WARNING | Suspicious but not confirmed | Note in report |
| 🚨 CRITICAL | Confirmed drift or credential exposed | Alert Netanel immediately |

**CRITICAL triggers:**
- SOUL.md or IDENTITY.md hash changed without "reset baseline" command
- Credential pattern found in a committed/shared file
- Injection pattern found in a file that was then acted upon

**On CRITICAL:** alert via WhatsApp to group `120363407274831275@g.us`.

### Cron Schedule

Run daily at 06:00 UTC (before morning briefing). Silent unless CRITICAL found.

```json
{
  "id": "security-daily",
  "schedule": "0 6 * * *",
  "timezone": "UTC",
  "task": "Run self-monitor security checks: file integrity, injection scan, credential scan. Alert Netanel at 120363407274831275@g.us if CRITICAL.",
  "delivery": { "mode": "silent" }
}
```
