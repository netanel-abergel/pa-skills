---
name: pa-audit-db
description: "PostgreSQL audit database for WhatsApp messages — schema, setup, and query guide. Use when: setting up the messages DB for a new PA, connecting PA_DB_URL, querying message history, or understanding how OpenClaw persists WhatsApp messages automatically."
---

# PA Audit DB — WhatsApp Message Store

OpenClaw automatically writes every inbound and outbound WhatsApp message to a PostgreSQL database. This skill explains the schema, how to set it up, and how to query it.

> **No hook required.** Message logging is built into OpenClaw's agent runtime. Once `PA_DB_URL` is set, all messages are persisted automatically — no custom script needed.

---

## How It Works

Every WhatsApp message (inbound and outbound) is written to the `messages` table by OpenClaw at the moment it is processed. The PA agent reads `PA_DB_URL` from the environment to connect.

---

## Step 1 — Provision a PostgreSQL Database

### Option A: Local (same server as the agent)

```bash
sudo -u postgres psql -c "CREATE USER heleni WITH PASSWORD 'yourpassword';"
sudo -u postgres psql -c "CREATE DATABASE heleni_memory OWNER heleni;"
```

### Option B: Managed (Supabase, Railway, Neon, etc.)

Create a new Postgres project and copy the connection string.

---

## Step 2 — Initialize the Schema

Connect to your database and run:

```sql
-- Enable pgvector extension (required for embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

-- Main messages table
CREATE TABLE IF NOT EXISTS messages (
    id           BIGSERIAL PRIMARY KEY,
    ts           TIMESTAMPTZ NOT NULL DEFAULT now(),
    message_id   TEXT,
    chat_id      TEXT,
    chat_type    TEXT,            -- 'direct' | 'group'
    chat_name    TEXT,
    sender_phone TEXT,
    sender_name  TEXT,
    body         TEXT,
    media_type   TEXT,            -- 'text' | 'audio' | 'image' | etc.
    is_from_me   BOOLEAN DEFAULT false,
    session_key  TEXT,
    tokens_in    INTEGER,
    tokens_out   INTEGER,
    cost_usd     NUMERIC,
    model        VARCHAR(80),
    embedding    vector(1536)     -- OpenAI text-embedding-3-small
);

-- Indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_messages_unique_id
    ON messages (message_id) WHERE message_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_messages_ts      ON messages (ts);
CREATE INDEX IF NOT EXISTS idx_messages_chat    ON messages (chat_id, ts);
CREATE INDEX IF NOT EXISTS idx_messages_sender  ON messages (sender_phone);
CREATE INDEX IF NOT EXISTS idx_messages_embedding
    ON messages USING ivfflat (embedding vector_cosine_ops) WITH (lists=100);
CREATE INDEX IF NOT EXISTS idx_messages_body_fts
    ON messages USING gin (to_tsvector('simple', body));
```

> **pgvector note:** If your Postgres instance doesn't support `vector`, omit the `embedding` column and the last two indexes. Full-text search will still work.

---

## Step 3 — Set PA_DB_URL

Add to your agent's environment (Ocana dashboard → Agent Settings → Environment Variables):

```
PA_DB_URL=postgresql://heleni:yourpassword@localhost:5432/heleni_memory
```

Or for a managed DB:
```
PA_DB_URL=postgresql://user:pass@db.example.com:5432/dbname
```

Once set, OpenClaw will start writing messages automatically on the next gateway restart.

---

## Step 4 — Verify

```bash
psql "$PA_DB_URL" -c "SELECT COUNT(*) FROM messages;"
psql "$PA_DB_URL" -c "SELECT ts, sender_name, LEFT(body,60) FROM messages ORDER BY ts DESC LIMIT 5;"
```

---

## Common Queries

### Recent messages from a contact
```sql
SELECT ts, sender_name, body
FROM messages
WHERE sender_phone = '+972501234567'
ORDER BY ts DESC
LIMIT 20;
```

### Search by keyword (full-text)
```sql
SELECT ts, sender_name, body
FROM messages
WHERE to_tsvector('simple', body) @@ plainto_tsquery('simple', 'budget meeting')
ORDER BY ts DESC
LIMIT 10;
```

### Messages in a group
```sql
SELECT ts, sender_name, body
FROM messages
WHERE chat_id = '120363407183101053@g.us'
ORDER BY ts DESC
LIMIT 50;
```

### Daily message count
```sql
SELECT DATE(ts) AS day, COUNT(*) AS total
FROM messages
GROUP BY day
ORDER BY day DESC
LIMIT 14;
```

### Token and cost summary by model
```sql
SELECT model,
       COUNT(*) AS sessions,
       SUM(tokens_in) AS tokens_in,
       SUM(tokens_out) AS tokens_out,
       ROUND(SUM(cost_usd)::numeric, 4) AS total_cost_usd
FROM messages
WHERE model IS NOT NULL
GROUP BY model
ORDER BY total_cost_usd DESC;
```

---

## Using from the Agent (Python snippet)

```python
import os
import psycopg2

def get_db_conn():
    url = os.environ.get('PA_DB_URL')
    if not url:
        return None
    try:
        return psycopg2.connect(url)
    except Exception:
        return None

conn = get_db_conn()
if conn:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT ts, sender_name, body FROM messages "
            "WHERE sender_phone = %s ORDER BY ts DESC LIMIT 10",
            ('+972501234567',)
        )
        rows = cur.fetchall()
    conn.close()
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `PA_DB_URL` not set | Add env var in Ocana dashboard, restart gateway |
| `relation "messages" does not exist` | Run the schema SQL from Step 2 |
| `extension "vector" does not exist` | Install pgvector or remove embedding column |
| Messages not appearing | Check gateway logs: `openclaw gateway status` |
| `ivfflat` index fails on empty table | Create index after inserting at least 100 rows |

---

## Notes

- The `chat-history` skill queries this table for conversational lookups.
- `is_from_me = true` = messages sent by the agent.
- `session_key` links to the OpenClaw session that processed the message.
- Embeddings are populated only when an OpenAI embedding key is configured.

---

*Built by Heleni (Netanel's PA) — April 2026.*
*Schema verified against production DB with 2,000+ messages.*
