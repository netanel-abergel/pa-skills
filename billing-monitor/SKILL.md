---
name: billing-monitor
description: "Monitor for API billing errors and alert the owner and admin immediately. Use when: an API billing error is detected, a peer PA reports a billing error, or during routine health checks. Handles detection, notification, and fallback model switching. Model-agnostic: works with any LLM provider (Anthropic, OpenAI, Google, etc.)."
---

# Billing Monitor Skill

Detect API billing errors early and respond automatically. Designed to be model-agnostic — adapt the detection and health-check commands to your LLM provider.

---

## Detection

### Error Signatures to Watch For

These patterns typically indicate billing or credit exhaustion:

```
your API key has run out of credits
insufficient balance
billing_error
payment_required
exceeded your current quota
HTTP 402
"error": {"type": "billing_error"}
```

### When to Run

- On any incoming message or tool call response that contains a billing error pattern
- During heartbeat health checks (every 2 hours recommended)
- After any failed LLM API call

---

## Response Protocol

When a billing error is detected, execute these steps **in order**:

### Step 1 — Notify Owner Immediately

Send this message to the owner via WhatsApp (or preferred channel):

```
⚠️ Billing issue — I'm unable to respond normally.
My API key has run out of credits (or been rate-limited).
Please top up or switch my API key in agent settings.
```

### Step 2 — Notify Admin

Send to your admin/network coordinator:

```
[PA Name] is reporting a billing error.
Owner: [Owner Name]
Action needed: top up API credits or reassign key.
Time detected: [timestamp]
```

### Step 3 — Attempt Fallback

If your agent supports model switching:
1. Check if a fallback model is configured in `config/billing-fallback.json`
2. Switch to fallback model
3. Notify owner of the temporary switch: "I've switched to [Fallback Model] temporarily while the primary key is resolved."
4. Log the switch

### Step 4 — Log the Incident

```bash
LOG_DIR="$HOME/.openclaw/workspace/logs"
mkdir -p "$LOG_DIR"

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) BILLING_ERROR api_key_exhausted" \
  >> "$LOG_DIR/billing-incidents.log"

echo "Logged billing error at $(date -u)"
```

---

## Health Check (Heartbeat Integration)

Add this to your heartbeat routine (every 2 hours):

```bash
#!/bin/bash
# billing-check.sh — Run during heartbeat to detect billing errors proactively

LOG_DIR="$HOME/.openclaw/workspace/logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

check_anthropic() {
  # Uses a minimal model from your Anthropic account — replace with the cheapest available
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "x-api-key: ${ANTHROPIC_API_KEY:-}" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d "{\"model\":\"${ANTHROPIC_CHECK_MODEL:-claude-haiku-20240307}\",\"max_tokens\":1,\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}]}" \
    https://api.anthropic.com/v1/messages 2>/dev/null)
  echo "$STATUS"
}

check_openai() {
  # Uses a minimal OpenAI model — replace with the cheapest available
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer ${OPENAI_API_KEY:-}" \
    -H "content-type: application/json" \
    -d "{\"model\":\"${OPENAI_CHECK_MODEL:-gpt-4o-mini}\",\"max_tokens\":1,\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}]}" \
    https://api.openai.com/v1/chat/completions 2>/dev/null)
  echo "$STATUS"
}

check_google() {
  # Uses Google Gemini API — requires GOOGLE_API_KEY env var
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://generativelanguage.googleapis.com/v1beta/models?key=${GOOGLE_API_KEY:-}" 2>/dev/null)
  echo "$STATUS"
}

# Detect which provider is configured — check in priority order
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  HTTP_STATUS=$(check_anthropic)
  PROVIDER="Anthropic"
elif [ -n "${OPENAI_API_KEY:-}" ]; then
  HTTP_STATUS=$(check_openai)
  PROVIDER="OpenAI"
elif [ -n "${GOOGLE_API_KEY:-}" ]; then
  HTTP_STATUS=$(check_google)
  PROVIDER="Google"
else
  echo "$TIMESTAMP SKIP no API key env vars set (checked ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY)" >> "$LOG_DIR/billing-incidents.log"
  exit 0
fi

case "$HTTP_STATUS" in
  200)
    echo "$TIMESTAMP OK $PROVIDER" >> "$LOG_DIR/billing-incidents.log"
    ;;
  402)
    echo "$TIMESTAMP BILLING_ERROR $PROVIDER HTTP_402" >> "$LOG_DIR/billing-incidents.log"
    echo "BILLING ERROR DETECTED — run billing response protocol"
    exit 1
    ;;
  401)
    echo "$TIMESTAMP AUTH_ERROR $PROVIDER HTTP_401_invalid_key" >> "$LOG_DIR/billing-incidents.log"
    echo "AUTH ERROR — invalid API key, notify admin"
    exit 1
    ;;
  429)
    echo "$TIMESTAMP RATE_LIMITED $PROVIDER HTTP_429" >> "$LOG_DIR/billing-incidents.log"
    echo "RATE LIMITED — temporary, retry in 60s"
    exit 2
    ;;
  *)
    echo "$TIMESTAMP UNKNOWN_ERROR $PROVIDER HTTP_$HTTP_STATUS" >> "$LOG_DIR/billing-incidents.log"
    echo "UNKNOWN ERROR HTTP $HTTP_STATUS"
    exit 1
    ;;
esac
```

**HTTP status codes:**
- `200` → OK, no billing issue
- `402` → Billing error (credits exhausted) → trigger protocol
- `401` → Invalid key → notify admin
- `429` → Rate limited → wait and retry (not a billing issue)

---

## Fallback Model Config

Store fallback configuration in `config/billing-fallback.json` (relative to workspace):

```json
{
  "primary_provider": "your-llm-provider",
  "primary_model": "your-primary-model",
  "fallback_provider": "your-fallback-provider",
  "fallback_model": "your-fallback-model",
  "fallback_api_key_env": "FALLBACK_PROVIDER_API_KEY",
  "admin_phone": "+1XXXXXXXXXX",
  "alert_channel": "whatsapp"
}
```

> **Examples:**
> - Anthropic primary + OpenAI fallback: `"primary_provider": "anthropic"`, `"primary_model": "claude-haiku-20240307"`, `"fallback_provider": "openai"`, `"fallback_model": "gpt-4o-mini"`
> - OpenAI primary + Google fallback: `"primary_provider": "openai"`, `"primary_model": "gpt-4o"`, `"fallback_provider": "google"`, `"fallback_model": "gemini-flash"`

### Switching to Fallback Model

```bash
#!/bin/bash
# switch-to-fallback.sh

FALLBACK_CONFIG="config/billing-fallback.json"

if [ ! -f "$FALLBACK_CONFIG" ]; then
  echo "ERROR: $FALLBACK_CONFIG not found. Cannot switch models."
  exit 1
fi

FALLBACK_MODEL=$(python3 -c "
import json
with open('$FALLBACK_CONFIG') as f:
    c = json.load(f)
print(c.get('fallback_model', ''))
")

if [ -z "$FALLBACK_MODEL" ]; then
  echo "ERROR: No fallback model configured in $FALLBACK_CONFIG"
  exit 1
fi

echo "Switching to fallback model: $FALLBACK_MODEL"
# Adjust this command to your OpenClaw agent configuration mechanism
openclaw config set model "$FALLBACK_MODEL" 2>/dev/null || \
  echo "WARNING: Could not auto-switch model. Manual update required in agent settings."
```

---

## Recovery

When billing is restored:

1. Owner confirms credits have been topped up
2. Switch back to primary model:
   ```bash
   openclaw config set model "$(python3 -c "import json; c=json.load(open('config/billing-fallback.json')); print(c['primary_model'])")"
   ```
3. Log recovery:
   ```bash
   echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) BILLING_RESTORED" >> logs/billing-incidents.log
   ```
4. Notify owner: "✅ Primary model restored. Normal service resumed."

---

## Edge Cases

| Scenario | Action |
|---|---|
| Rate limit (429), not billing | Wait 60s, retry. Do not trigger billing protocol. |
| Intermittent 5xx error | Retry 2x with 10s delay. If persists, treat as outage and notify owner. |
| Both primary and fallback billing errors | Escalate to admin immediately. Agent cannot function. |
| Billing error during a critical task | Finish with fallback if possible; otherwise pause and notify. |
| API key env var not set | Log as config issue, notify admin to set the env var. |
| Peer PA reports billing error | Log, add to status report, notify admin if you are the network coordinator. |

---

## Model Guidance

This skill does not require a sophisticated LLM — detection and alerting are rule-based. The LLM is only needed for:
- Composing the notification message to the owner (any model works)
- Deciding whether to switch models based on config (simple logic)

If the primary model is down due to billing, the fallback model handles these tasks.
