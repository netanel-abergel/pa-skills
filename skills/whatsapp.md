# WhatsApp Agent Plugin

Full WhatsApp integration for AI agents - not just messaging, but cross-group awareness, persistent message history in PostgreSQL, and total recall across every conversation.

GitHub repo: https://github.com/novalystrix/whatsapp-agent-plugin

## What This Actually Does

Most WhatsApp integrations let you send and receive messages. This plugin makes your agent aware - it knows what's happening across all your WhatsApp groups simultaneously, remembers every message ever sent, and can search and reference past conversations on demand.

## Core Capabilities
- Multi-group awareness - Monitor all WhatsApp groups simultaneously from a single agent session
- Cross-group context - Agent maintains awareness of conversations across groups, even when they're isolated into separate sessions
- PostgreSQL audit log - Every message (inbound and outbound) stored with full metadata: sender, timestamp, chat type, media type, tokens, cost
- Full-text search - GIN-indexed message search across all conversations
- Message recall - Agent can reference any past conversation, quote specific messages, and maintain continuity across sessions
- Reply threading - Native WhatsApp reply/quote support with [[reply_to:<message_id>]]
- Media support - Images, documents, audio, video - send and receive
- Group engagement rules - Configurable behavior: scan-only mode, respond-when-tagged, or full participation

## Architecture

┌─────────────────────────────────────────────────┐
│                   AI Agent (OpenClaw)          │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ WhatsApp  │  │ Cross-Group  │  │   Audit   │ │
│  │ Channel   │  │  Awareness   │  │    Log    │ │
│  │ (baileys) │  │  (heartbeat) │  │   (PG)    │ │
│  └─────┬─────┘  └──────┬───────┘  └─────┬─────┘ │
└────────┼───────────────┼────────────────┼────────┘
         │               │                │
    ┌────▼────┐    ┌─────▼─────┐    ┌─────▼──────┐
    │WhatsApp │    │ Gateway   │    │ PostgreSQL │
    │  (WA    │    │   Logs    │    │  messages  │
    │ Web API)│    │ (JSON)    │    │   table    │
    └─────────┘    └───────────┘    └────────────┘

## Included Skills

### 1. Cross-Group Awareness
On every heartbeat, scans gateway logs for all group activity, builds a context file with recent messages per group, and gives the agent a birds-eye view across all groups.

### 2. Chat History / Audit Log
Every message flows through PostgreSQL. Full-text search, search by chat/sender/date, reply to past messages, and per-message LLM cost tracking.

## Setup
See the full README at https://github.com/novalystrix/whatsapp-agent-plugin for PostgreSQL schema, skill installation, and configuration.
