---
name: whatsapp-diagnostics
description: "Diagnose and fix WhatsApp connectivity issues for OpenClaw agents. Use when: a PA is not responding, WhatsApp shows connected but messages don't arrive, the agent is online but not replying, or troubleshooting a new agent setup."
---

# WhatsApp Diagnostics Skill

Systematic diagnosis for WhatsApp connectivity issues in OpenClaw agents.

---

## Diagnostic Tree

```
PA not responding?
│
├─ Dashboard shows "Connected and listening"?
│   ├─ YES → Check Messages count
│   │   ├─ Messages = 0 → INGEST ISSUE (messages not reaching agent)
│   │   └─ Messages > 0 → RUNTIME ISSUE (agent receives but doesn't reply)
│   └─ NO → CONNECTION ISSUE (WhatsApp itself not linked)
│
└─ Agent exists in platform?
    ├─ YES → Check channel configuration
    └─ NO → Full setup needed
```

---

## Case 1: Connection Issue (WhatsApp not linked)

**Symptoms:** Dashboard shows disconnected, no QR code, channel error

**Steps:**
1. Open agent settings in OpenClaw platform
2. Go to Channels → WhatsApp
3. Click "Connect" or "Re-link"
4. Scan QR code with WhatsApp Business app
5. Verify phone number matches
6. Wait 30 seconds for status to update

**Common cause:** WhatsApp session expired (happens after ~14 days of inactivity or phone restart)

---

## Case 2: Ingest Issue (Connected + Messages = 0)

**Symptoms:** Dashboard shows "Connected and listening", messages count stays 0 after sending

**This means:** WhatsApp is connected at the protocol level, but messages are not reaching the agent runtime.

**Steps:**
1. Check OpenClaw gateway status:
   ```bash
   openclaw gateway status
   ```
2. Restart the gateway:
   ```bash
   openclaw gateway restart
   ```
3. Send a test message and wait 30 seconds
4. If still 0 → check gateway logs:
   ```bash
   openclaw gateway logs --last 50
   ```
5. Look for errors: `binding failed`, `session dropped`, `ingest error`
6. If unresolved → escalate to platform admin (this is an infrastructure issue)

---

## Case 3: Runtime Issue (Messages arriving, no reply)

**Symptoms:** Messages count increments, but agent doesn't respond

**This means:** Messages reach the agent, but something is wrong with the agent runtime.

**Steps:**
1. Check for billing error:
   ```bash
   grep -i "billing\|402\|credits" ~/.openclaw/logs/agent.log | tail -20
   ```
2. Check model configuration:
   ```bash
   openclaw status
   ```
3. Check if API key is valid (use the command matching your LLM provider):
   ```bash
   # For Anthropic
   curl -s -o /dev/null -w "%{http_code}" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     https://api.anthropic.com/v1/models
   # Expected: 200. If 401 → invalid key. If 402 → billing.

   # For OpenAI
   curl -s -o /dev/null -w "%{http_code}" \
     -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

   # For Google
   curl -s -o /dev/null -w "%{http_code}" \
     "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY"
   ```
4. Check recent errors:
   ```bash
   openclaw logs --last 100 | grep -i error
   ```

---

## Quick Health Check Script

```bash
#!/bin/bash
# whatsapp-health-check.sh
# Model-agnostic: checks whichever LLM provider API key is configured
set -e

echo "=== WhatsApp Diagnostics ==="

echo -n "Gateway status: "
openclaw gateway status 2>&1 | grep -o "running\|stopped\|error" | head -1 || echo "unknown"

echo -n "API key valid: "
check_api_key() {
  if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
      -H "x-api-key: ${ANTHROPIC_API_KEY}" \
      -H "anthropic-version: 2023-06-01" \
      https://api.anthropic.com/v1/models 2>/dev/null)
    PROVIDER="Anthropic"
  elif [ -n "${OPENAI_API_KEY:-}" ]; then
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
      -H "Authorization: Bearer ${OPENAI_API_KEY}" \
      https://api.openai.com/v1/models 2>/dev/null)
    PROVIDER="OpenAI"
  elif [ -n "${GOOGLE_API_KEY:-}" ]; then
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
      "https://generativelanguage.googleapis.com/v1beta/models?key=${GOOGLE_API_KEY}" 2>/dev/null)
    PROVIDER="Google"
  else
    echo "⚠️ no API key env var found (checked ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY)"
    return
  fi
  case $STATUS in
    200) echo "✅ valid ($PROVIDER)" ;;
    401) echo "❌ invalid key ($PROVIDER)" ;;
    402) echo "⚠️ billing error ($PROVIDER)" ;;
    *)   echo "? HTTP $STATUS ($PROVIDER)" ;;
  esac
}
check_api_key

echo -n "Recent errors: "
ERROR_COUNT=$(openclaw logs --last 100 2>/dev/null | grep -ic error || echo 0)
echo "$ERROR_COUNT found"

echo "=== Done ==="
```

---

## Escalation

Escalate to platform admin if:
- Gateway restarts don't fix Messages=0
- Errors mention `socket`, `binding`, or `session` issues
- Multiple agents on the same server affected simultaneously

Include in escalation report:
- Agent name
- Phone number
- Time issue started
- Dashboard screenshot (Connected state + Messages count)
- Output of `openclaw gateway status`

---

## Prevention

- **Keep WhatsApp active:** Send at least one message every 7 days to prevent session expiry
- **Monitor with heartbeat:** Check Messages count during heartbeat routine
- **Backup phone number:** Note the phone number used — needed for re-linking
- **Don't use same number on two devices:** WhatsApp only allows one active session

---

## Model Compatibility

This skill is entirely model-agnostic. All diagnostics are CLI-based (bash commands, curl, openclaw CLI) — the LLM is only used to interpret outputs and decide which step to take next.

- Any LLM model is sufficient for following this decision tree
- The API key check commands in Case 3 cover Anthropic, OpenAI, and Google — adapt to your provider
- No provider-specific reasoning is required
