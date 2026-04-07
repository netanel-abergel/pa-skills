# message-history-setup

Set up the PostgreSQL message history database for your PA agent. Enables full conversation recall across sessions — every inbound and outbound WhatsApp message is logged automatically by the Ocana platform.

## When to Use
- First-time setup of a new PA agent
- Message history is not being logged (`chat-history` queries return empty)
- `PA_DB_URL` is missing or misconfigured
- Verifying the DB is receiving messages after setup

---

## How It Works

The Ocana platform writes every inbound and outbound WhatsApp message to a PostgreSQL database automatically — **no external hook or custom script needed**. The only requirement is:

1. PostgreSQL is running and accessible
2. The `messages` table exists with the correct schema
3. `PA_DB_URL` is set in the agent's environment

Once configured, the DB grows automatically with every message. Use the `chat-history` skill to query it.

---

## Step 1 — Install PostgreSQL

```bash
sudo apt-get update && sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

---

## Step 2 — Create DB and User

```bash
sudo -u postgres psql << 'EOF'
CREATE DATABASE janet_memory;
CREATE USER janet WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE janet_memory TO janet;
\c janet_memory
GRANT ALL ON SCHEMA public TO janet;
EOF
```

> Replace `janet` and `janet_memory` with your agent name if preferred.

---

## Step 3 — Apply Schema

```bash
psql "postgresql://janet:your_secure_password@localhost:5432/janet_memory" \
  -f /opt/ocana/openclaw/audit-log-schema.sql
```

The schema file ships with OpenClaw at `/opt/ocana/openclaw/audit-log-schema.sql`.

### Table: `messages`

| Column | Type | Description |
|---|---|---|
| `id` | serial | Auto-increment primary key |
| `ts` | timestamptz | Message timestamp |
| `message_id` | text | WhatsApp message ID |
| `chat_id` | text | Group JID or phone number |
| `sender_phone` | text | Sender E.164 |
| `sender_name` | text | Display name |
| `body` | text | Message content |
| `is_from_me` | bool | True if sent by agent |
| `model` | text | LLM model used (if agent reply) |
| `tokens` | int | Token count (if agent reply) |
| `cost` | numeric | Estimated cost (if agent reply) |

Full-text search index and optional vector embeddings (1536-dim) are applied automatically by the schema.

---

## Step 4 — Set PA_DB_URL

Add to your OpenClaw config (`openclaw.json`) under hooks:

```json
{
  "hooks": {
    "internal": {
      "entries": {
        "wa-audit-log": {
          "env": {
            "PA_DB_URL": "postgresql://janet:your_secure_password@localhost:5432/janet_memory"
          }
        }
      }
    }
  }
}
```

Or set as an environment variable:

```bash
export PA_DB_URL="postgresql://janet:your_secure_password@localhost:5432/janet_memory"
```

---

## Step 5 — Verify

Send a test message to your agent, then check:

```bash
psql "postgresql://janet:your_secure_password@localhost:5432/janet_memory" \
  -c "SELECT id, ts, sender_name, LEFT(body, 60) FROM messages ORDER BY ts DESC LIMIT 5;"
```

If rows appear, the setup is complete.

---

## Troubleshooting

**No rows appearing:**
- Confirm `PA_DB_URL` is set correctly in the config
- Check the gateway is running and not in a crash loop
- Verify the `messages` table exists: `\dt` in psql

**psycopg2 not installed (for Python queries):**
```bash
pip3 install psycopg2-binary
```

**Permission errors:**
```bash
sudo -u postgres psql -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO janet;"
sudo -u postgres psql -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO janet;"
```

---

## Next Step

Once the DB is running, install the `chat-history` skill to query past conversations.

## Credit

Setup guide authored by Janet (Gabriel Amram's PA) — April 2026.
Based on implementation by Heleni, running in production with 2,000+ messages logged.
