# PA Message History Database Guide

> How to give your PA a searchable memory of every WhatsApp conversation.

---

## Why a Message DB?

Without a DB, your PA can only remember what's in its context files — a short-term, per-conversation log that gets overwritten. With a PostgreSQL database:

- 🔍 **Search any past message** by keyword, contact, or date
- 📊 **Track unanswered messages** across all chats
- 🧠 **Skills become smarter** — they query history instead of guessing
- 📈 **Cost visibility** — see which conversations drive the most token spend

Skills that benefit: `chat-history`, `heleni-whatsapp`, `supervisor`, `pa-status`, `owner-briefing`

---

## Setup (~10 min)

### Step 1 — Install PostgreSQL

```bash
sudo apt-get install -y postgresql python3-psycopg2
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### Step 2 — Create DB and User

```bash
sudo -u postgres psql <<EOF
CREATE USER heleni WITH PASSWORD 'your_password_here';
CREATE DATABASE heleni_memory OWNER heleni;
GRANT ALL PRIVILEGES ON DATABASE heleni_memory TO heleni;
EOF
```

### Step 3 — Apply Schema

```bash
sudo -u postgres psql heleni_memory < /path/to/openclaw/audit-log-schema.sql
```

This creates the `messages` table with full-text search indexes.

### Step 4 — Enable the Hook in openclaw.json

Find the `hooks → internal → entries` section and add/update `wa-audit-log`:

```json
"wa-audit-log": {
  "enabled": true,
  "env": {
    "PA_DB_URL": "postgresql://heleni:your_password_here@localhost:5432/heleni_memory"
  }
}
```

### Step 5 — Restart Gateway

```bash
openclaw gateway restart
```

From now on, every inbound and outbound WhatsApp message is automatically logged.

---

## Verify It's Working

```bash
PGPASSWORD=your_password_here psql -h localhost -U heleni -d heleni_memory -c \
  "SELECT COUNT(*), MIN(ts), MAX(ts) FROM messages;"
```

After a few messages: you should see rows appearing in real time.

---

## The `PA_DB_URL` Standard

All PA skills use a single env var: `PA_DB_URL`.

Skills detect it automatically:
```python
import os, psycopg2

url = os.environ.get('PA_DB_URL')
if url:
    conn = psycopg2.connect(url)
    # DB mode — full power
else:
    # File fallback — context files only
```

This means: **the same skill works on any PA**, with or without a DB. No config changes needed per skill.

---

## DB Schema Reference

```sql
CREATE TABLE messages (
  id          BIGSERIAL PRIMARY KEY,
  ts          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  message_id  TEXT,              -- WhatsApp message ID (deduplicated)
  chat_id     TEXT,              -- Phone number or group JID
  chat_type   TEXT,              -- 'direct' | 'group'
  chat_name   TEXT,              -- Group name or contact name
  sender_phone TEXT,
  sender_name  TEXT,
  body        TEXT,              -- Message text
  media_type  TEXT,              -- 'image' | 'audio' | 'document' | NULL
  is_from_me  BOOLEAN,           -- true = PA sent it
  session_key TEXT,              -- OpenClaw session reference
  tokens_in   INTEGER,
  tokens_out  INTEGER,
  cost_usd    NUMERIC,
  model       VARCHAR(80)
);
```

Indexes: full-text search on body, chat+time lookup, sender lookup, deduplication on message_id.

---

## Common Queries

### Find what was said about a topic
```python
cur.execute("""
  SELECT ts, sender_name, chat_name, body
  FROM messages
  WHERE to_tsvector('simple', body) @@ plainto_tsquery('simple', %s)
  ORDER BY ts DESC LIMIT 20
""", ("budget",))
```

### Get all messages from a contact
```python
cur.execute("""
  SELECT ts, body, is_from_me
  FROM messages
  WHERE chat_id = %s
  ORDER BY ts DESC LIMIT 50
""", ("+1234567890",))
```

### Find unanswered messages (last 24h)
```python
cur.execute("""
  SELECT DISTINCT ON (chat_id) chat_id, chat_name, sender_name, body, ts
  FROM messages
  WHERE is_from_me = false
    AND ts > NOW() - INTERVAL '24 hours'
    AND chat_id NOT IN (
      SELECT DISTINCT chat_id FROM messages
      WHERE is_from_me = true AND ts > NOW() - INTERVAL '24 hours'
    )
  ORDER BY chat_id, ts DESC
""")
```

### Daily stats
```python
cur.execute("""
  SELECT COUNT(*) FILTER (WHERE NOT is_from_me) as inbound,
         COUNT(*) FILTER (WHERE is_from_me) as outbound,
         COUNT(DISTINCT chat_id) as active_chats
  FROM messages
  WHERE ts > NOW() - INTERVAL '24 hours'
""")
```

---

## Backfilling Historical Messages

If your PA has been running for a while without a DB, you can import history from OpenClaw session files:

```python
#!/usr/bin/env python3
"""
Backfill historical WhatsApp messages from OpenClaw session files to PostgreSQL.
Run once after DB setup.
"""
import json, os, re, psycopg2
from datetime import datetime, timezone

DB_URL = os.environ.get('PA_DB_URL')
SESSIONS_DIR = '/path/to/openclaw/agents/main/sessions'

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

with open(f'{SESSIONS_DIR}/sessions.json') as f:
    sessions = json.load(f)

inserted = 0
for key, sess in sessions.items():
    if 'whatsapp' not in key:
        continue
    sf = sess.get('sessionFile')
    if not sf or not os.path.exists(sf):
        continue
    
    # Parse chat_id and type from session key
    parts = key.split(':')
    chat_type = 'group' if 'group' in key else 'direct'
    chat_id = parts[-1]
    
    with open(sf) as f:
        for line in f:
            try:
                r = json.loads(line)
                if r.get('type') != 'message':
                    continue
                msg = r.get('message', {})
                role = msg.get('role')
                if role not in ('user', 'assistant'):
                    continue
                
                # Extract text content
                body = ''
                msg_id = None
                for c in msg.get('content', []):
                    if c.get('type') == 'text':
                        text = c['text']
                        # Extract message_id from metadata
                        m = re.search(r'"message_id":\s*"([^"]+)"', text)
                        if m:
                            msg_id = m.group(1)
                        # Extract actual message (after metadata blocks)
                        parts_text = re.split(r'```\s*\n', text)
                        body = parts_text[-1].strip() if len(parts_text) > 1 else text.strip()
                        break
                
                if not body:
                    continue
                
                ts = datetime.fromtimestamp(r['timestamp'] / 1000, tz=timezone.utc)
                is_from_me = (role == 'assistant')
                
                cur.execute("""
                    INSERT INTO messages (ts, message_id, chat_id, chat_type, body, is_from_me)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (message_id) WHERE message_id IS NOT NULL DO NOTHING
                """, (ts, msg_id, chat_id, chat_type, body, is_from_me))
                inserted += 1
            except Exception:
                pass

conn.commit()
print(f"Imported {inserted} messages")
```

---

## Skills That Use PA_DB_URL

| Skill | DB Feature |
|-------|-----------|
| `chat-history` | Full-text search, contact search, date range |
| `heleni-whatsapp` | Unanswered message detection |
| `supervisor` | DB health stats |
| `pa-status` | Per-PA DB connectivity check |
| `owner-briefing` | (future) message highlights |

---

## Troubleshooting

**Hook not logging messages:**
```bash
# Check hook is enabled
cat /path/to/openclaw/openclaw.json | python3 -c "
import json,sys; d=json.load(sys.stdin)
hook = d['hooks']['internal']['entries'].get('wa-audit-log', {})
print('enabled:', hook.get('enabled'))
print('env keys:', list(hook.get('env', {}).keys()))
"
```

**Can't connect to DB:**
```bash
python3 -c "import psycopg2; psycopg2.connect('$PA_DB_URL').close(); print('OK')"
```

**psycopg2 not installed:**
```bash
sudo apt-get install python3-psycopg2
# or: pip3 install psycopg2-binary
```
