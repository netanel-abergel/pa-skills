# @ai-pa/billing-monitor

OpenClaw plugin that monitors API billing health and alerts on failures.

## Install

```
openclaw plugin install @ai-pa/billing-monitor
```

## Config

In openclaw.json:
```json
{
  "plugins": {
    "entries": {
      "ai-pa-billing-monitor": {
        "enabled": true,
        "config": {
          "adminPhone": "+1XXXXXXXXXX",
          "checkInterval": 60
        }
      }
    }
  }
}
```

## What it does

- Checks Anthropic and OpenAI API key status on every heartbeat
- If billing error (402) → sends WhatsApp alert to adminPhone
- If invalid key (401) → logs to agent output
- Zero config required — auto-detects keys from env vars
