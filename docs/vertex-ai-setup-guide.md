# Vertex AI Setup Guide for OpenClaw PAs

How to connect an OpenClaw agent to Claude models via Google Vertex AI, using the same architecture as Heleni.

---

## Architecture Overview

```
OpenClaw Agent
    ↓ (vertex_ai provider, localhost:4000)
LiteLLM Proxy (Docker)
    ↓ (Google ADC credentials)
Vertex AI (us-east5)
    ↓
Claude Sonnet / Opus
```

- **LiteLLM** runs as a local Docker container, proxying OpenClaw requests to Vertex AI
- **OpenClaw** talks to LiteLLM as if it were a standard OpenAI-compatible API
- **Credentials** are Google ADC (authorized_user or service_account), mounted into the container

---

## Prerequisites

1. A Google Cloud project with **Vertex AI API enabled**
2. ADC credentials (authorized_user or service_account JSON) with access to that project
3. Docker installed on the host
4. OpenClaw installed

---

## Step 1: Prepare Credentials

Create a directory for Vertex files:
```bash
sudo mkdir -p /opt/ocana/vertex
```

Write your credentials file:
```bash
cat > /opt/ocana/vertex/credentials.json << 'EOF'
{
  "type": "authorized_user",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "refresh_token": "YOUR_REFRESH_TOKEN",
  "universe_domain": "googleapis.com"
}
EOF
chmod 600 /opt/ocana/vertex/credentials.json
```

> **Alternative**: Use a service_account JSON instead of authorized_user for production. Same file path, different JSON structure.

---

## Step 2: Create LiteLLM Config

```bash
cat > /opt/ocana/vertex/config.yaml << 'EOF'
model_list:
  - model_name: claude-sonnet-4-6-20250514
    litellm_params:
      model: vertex_ai/claude-sonnet-4-6
      vertex_project: YOUR_PROJECT_ID
      vertex_location: us-east5
      timeout: 30
      stream_timeout: 10
  - model_name: claude-opus-4-6-20250514
    litellm_params:
      model: vertex_ai/claude-opus-4-6
      vertex_project: YOUR_PROJECT_ID
      vertex_location: us-east5
      timeout: 30
      stream_timeout: 10

litellm_settings:
  cache: False

router_settings:
  routing_strategy: "latency-based-routing"
  routing_strategy_args:
    ttl: 30
  num_retries: 1
  timeout: 30
EOF
```

Replace `YOUR_PROJECT_ID` with your GCP project ID (e.g., `devex-ai`).

> **Note**: `us-central1` is NOT supported for Claude models on Vertex as of April 2026. Use `us-east5`.

> **Cache**: Set `cache: False` unless you have a Redis instance. Heleni uses Redis but it's optional.

---

## Step 3: Start LiteLLM Docker Container

```bash
docker run -d \
  --name ocana-litellm-proxy \
  --restart unless-stopped \
  -p 4000:4000 \
  -v /opt/ocana/vertex:/opt/vertex \
  -e GOOGLE_APPLICATION_CREDENTIALS=/opt/vertex/credentials.json \
  -e LITELLM_MASTER_KEY=sk-your-local-proxy-key \
  -e LITELLM_LOCAL_MODEL_COST_MAP=True \
  -e LITELLM_LOG=INFO \
  ghcr.io/berriai/litellm:v1.82.3-stable \
  --config /opt/vertex/config.yaml
```

Replace `sk-your-local-proxy-key` with any secret string — this is the local API key OpenClaw will use to talk to LiteLLM.

Wait ~10 seconds for startup, then verify:
```bash
docker logs --tail 20 ocana-litellm-proxy
```

You should see the model list and "Uvicorn running on http://0.0.0.0:4000".

---

## Step 4: Verify LiteLLM Access

```bash
curl -s http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-your-local-proxy-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-6-20250514",
    "messages": [{"role": "user", "content": "Reply with exactly OK"}],
    "max_tokens": 8
  }' | python3 -m json.tool
```

Expected: a response with `"content": "OK"`.

---

## Step 5: Configure OpenClaw

Add the vertex_ai provider to OpenClaw config:

```bash
openclaw config set models.providers.vertex_ai.baseUrl "http://localhost:4000/v1" --strict-json
openclaw config set models.providers.vertex_ai.apiKey "sk-your-local-proxy-key" --strict-json
```

Or edit `$OPENCLAW_HOME/openclaw.json` directly and add under `models.providers`:

```json
"vertex_ai": {
  "apiKey": "sk-your-local-proxy-key",
  "baseUrl": "http://localhost:4000/v1",
  "models": [
    { "id": "claude-sonnet-4-6-20250514", "name": "claude-sonnet-4-6-20250514" },
    { "id": "claude-opus-4-6-20250514", "name": "claude-opus-4-6-20250514" }
  ]
}
```

---

## Step 6: Set Default Model

For **main sessions** (opus):
```bash
openclaw models set vertex_ai/claude-opus-4-6-20250514
```

For **crons and subagents** (sonnet — cheaper):
Set `payload.model` to `vertex_ai/claude-sonnet-4-6-20250514` in each cron job.

---

## Step 7: Verify End-to-End

```bash
openclaw config get agents.defaults.model
# Should show: vertex_ai/claude-opus-4-6-20250514

openclaw doctor --fix
```

Send a test message to the agent and check that it responds.

---

## Dynamic Model Routing (Recommended)

Use opus for owner conversations, sonnet for background work:

| Context | Model | Reason |
|---|---|---|
| Main session (owner DM) | opus | Best judgment, nuance |
| Crons | sonnet | Cost-effective, good enough |
| Subagents | sonnet | Parallel work, lower cost |
| Groups | sonnet or opus | Depends on complexity |

Opus costs ~5x more than sonnet per token.

---

## Troubleshooting

### "Quota exceeded" (429)
The model exists but your project needs quota. Request increase at:
```
https://console.cloud.google.com/iam-admin/quotas?project=YOUR_PROJECT_ID
```
Filter by base model name (e.g., `anthropic-claude-opus-4-6`).

### "Not servable in region" (400)
Use `us-east5` only. `us-central1` does NOT support Claude models.

### "Permission denied" (403)
The credentials don't have access to the project. Check:
- Is Vertex AI API enabled? (`aiplatform.googleapis.com`)
- Does the user/SA have `roles/aiplatform.user`?

### LiteLLM container won't start
```bash
docker logs ocana-litellm-proxy
```
Common: bad YAML syntax, missing credentials file, wrong mount path.

### Redis timeout errors (non-blocking)
If you see Redis timeout warnings in LiteLLM logs, set `cache: False` in config.yaml and restart the container. Caching is optional.

### OpenClaw still using old model
Existing sessions keep their model until reset. New sessions pick up the new default. To force:
- Start a new conversation, or
- Reset the session from the OpenClaw web UI

---

## Quick Reference

| Item | Value |
|---|---|
| LiteLLM image | `ghcr.io/berriai/litellm:v1.82.3-stable` |
| Proxy port | `4000` |
| Credentials path (container) | `/opt/vertex/credentials.json` |
| Config path (container) | `/opt/vertex/config.yaml` |
| Vertex region | `us-east5` |
| OpenClaw provider name | `vertex_ai` |
| Sonnet model ID | `claude-sonnet-4-6-20250514` |
| Opus model ID | `claude-opus-4-6-20250514` |

---

## For PA Onboarding

When helping another PA set up Vertex:

1. Get their GCP project ID and credentials from the owner
2. Walk through Steps 1-7 above
3. Start with **sonnet only** — it's cheaper and sufficient for most PA work
4. Add opus later if needed for the owner's main session
5. Verify with the smoke test in Step 4 before touching OpenClaw config
6. **Never set the default model before verifying access** — always test the LiteLLM route first
