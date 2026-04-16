# Chat History / Audit Log

Search and reference past conversations from a PostgreSQL audit log database.

## What It Does
Every message the agent sends and receives is stored in a PostgreSQL audit log. The agent can:
- Recall past conversations
- Reference earlier decisions
- Search by keyword, date, sender, or chat
- Maintain continuity across sessions
- Quote specific past messages

## Database Schema

### Messages Table
| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Auto-increment PK |
| ts | timestamptz | Message timestamp |
| message_id | text | Platform message ID |
| chat_id | text | Chat identifier |
| chat_type | text | direct / group / device |
| chat_name | text | Group name or chat label |
| sender_phone | text | Sender phone number |
| sender_name | text | Sender display name |
| body | text | Message text content |
| media_type | text | image/audio/etc or null |
| is_from_me | boolean | true = agent's messages |

## Query Patterns

### Full-text search (preferred)
SELECT id, ts, chat_name, sender_name, LEFT(body, 200)
FROM messages
WHERE to_tsvector('simple', body) @@ plainto_tsquery('simple', 'search terms')
ORDER BY ts DESC LIMIT 20;

### Search by date range
SELECT id, ts, chat_name, sender_name, LEFT(body, 200)
FROM messages WHERE ts BETWEEN '2026-02-20' AND '2026-02-21'
ORDER BY ts LIMIT 50;

### Get conversation context
SELECT id, ts, sender_name, LEFT(body, 300)
FROM messages WHERE id BETWEEN (TARGET_ID - 5) AND (TARGET_ID + 5)
ORDER BY ts;

## Setup
1. PostgreSQL database with the messages table and indexes
2. Full-text search index: GIN on to_tsvector('simple', body)
3. Indexes on chat_id+ts, sender_phone, ts for fast lookups
4. Ingest pipeline that writes messages to the table in real-time

## Tips
- Always add LIMIT to queries
- is_from_me = true -> agent sent it
- is_from_me = false -> a human sent it
- Use full-text search for keyword queries (faster than ILIKE)
- Use ILIKE for exact phrase matching
