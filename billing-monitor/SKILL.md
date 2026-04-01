---
name: billing-monitor
description: "Monitor for API billing errors and alert the owner and admin immediately. Use when: an API billing error is detected, a peer PA reports a billing error, or during routine health checks. Handles detection, notification, and fallback model switching."
---

# Billing Monitor Skill

Detect API billing errors early and respond automatically.

---

## Detection

### Error Signatures to Watch For

```
⚠️ API provider returned a billing error
your API key has run out of credits
insufficient balance
billing_error
payment_required
402
```

### When to Run

- On any incoming message that contains a billing error pattern
- During heartbeat health checks
- After any failed tool call

---

## Response Protocol

When a billing error is detected:

### Step 1 — Notify Owner Immediately

```
Message to owner:
"⚠️ Billing issue — I'm unable to respond normally.
My API key has run out of credits.
Please top up or switch my API key in agent settings."
```

### Step 2 — Notify Admin

```
Message to your admin/network coordinator:
"[PA Name] is reporting a billing error.
Owner: [Owner Name] ([Owner Phone])
Action needed: top up API credits or reassign key."
```

### Step 3 — Attempt Fallback

If your agent supports model switching:
1. Check if an alternative model is configured
2. Switch to fallback model (e.g. GPT-4o if Claude fails)
3. Notify owner of the temporary switch

### Step 4 — Log the Incident

```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) BILLING_ERROR api_key_exhausted" \
  >> ~/.openclaw/workspace/logs/billing-incidents.log
```

---

## Health Check (Heartbeat Integration)

Add to your heartbeat routine:

```
Every 2 hours:
1. Send a minimal test query to your API provider
2. If 402/billing error → run billing response protocol
3. Log result to billing-incidents.log
```

Test query (Anthropic):
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-haiku-20240307","max_tokens":1,"messages":[{"role":"user","content":"ping"}]}' \
  https://api.anthropic.com/v1/messages
```
- `200` → OK
- `402` → Billing error → trigger protocol
- `401` → Invalid key → notify admin

---

## Fallback Model Config

Store fallback in `~/.openclaw/workspace/config/billing-fallback.json`:

```json
{
  "primary_model": "claude-sonnet-4-6",
  "fallback_model": "gpt-4o-mini",
  "fallback_api_key_env": "OPENAI_API_KEY",
  "admin_phone": "+1XXXXXXXXXX",
  "alert_channel": "whatsapp"
}
```

---

## Recovery

When billing is restored:
1. Owner confirms credits topped up
2. Switch back to primary model
3. Log recovery: `BILLING_RESTORED`
4. Notify owner that normal service is resumed
