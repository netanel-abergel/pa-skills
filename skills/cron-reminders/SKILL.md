# Cron Reminders Skill

> **When to use this vs `quick-reminders`:**
> - `quick-reminders` uses `nohup sleep` — great for reminders within a few hours, but **does not survive server reboots**. Best for same-day, short-horizon reminders.
> - `cron-reminders` (this skill) uses a persistent JSON file + a cron job — **survives reboots**, handles reminders days, weeks, or months out. Best for long-dated reminders and project touchpoints.
>
> You can run both side by side.

**Trigger:** When the owner asks to be reminded of something at a specific date/time, especially more than a few hours away.

**Examples:**
- "Remind me on April 20th at 10am to follow up with the team"
- "Set a reminder for next Monday to check the Redis board"
- "Remind me in 3 weeks to review the epics"

---

## How It Works

- **Storage:** `data/reminders.json` in workspace — one entry per reminder, fully auditable
- **Execution:** A cron job runs every 15 minutes and fires any reminder whose `datetime` falls within the last 15-minute window
- **Delivery:** Via `openclaw message send` — WhatsApp, Telegram, Slack, etc.
- **Survives reboots:** Yes — cron is persistent, JSON file is on disk

---

## Setup

### 1. Copy config
```bash
cp skills/cron-reminders/.context.example skills/cron-reminders/.context
# Edit .context with your owner's phone number, channel, and timezone
```

### 2. Make script executable
```bash
chmod +x skills/cron-reminders/scripts/check-reminders.sh
```

### 3. Add cron job
```bash
# Runs every 15 minutes
(crontab -l 2>/dev/null; echo "*/15 * * * * /path/to/workspace/skills/cron-reminders/scripts/check-reminders.sh >> /path/to/workspace/logs/reminders.log 2>&1") | crontab -
```

> **Tip:** Adjust the script path to your actual workspace location.

---

## JSON Format (`data/reminders.json`)

```json
[
  {
    "id": "call-mom-apr7",
    "datetime": "2026-04-07T13:00:00",
    "channel": "whatsapp",
    "target": "+972XXXXXXXXX",
    "message": "Hey — call mom 📞"
  }
]
```

- `datetime`: Local time in owner's timezone (not UTC). Set timezone in `.context`.
- `channel`: `whatsapp`, `telegram`, `slack`, etc.
- `target`: E.164 for WhatsApp/Signal, chat ID for Telegram, etc.
- `message`: Composed at creation time — should make sense out of context.

---

## PA Workflow

When owner says "remind me X on Y at Z":

1. Extract: message, date, time (default: 12:00 local time if no hour given)
2. Add entry to `data/reminders.json`
3. Confirm briefly — e.g. "Done, Apr 20 at 10am"

**Default time:** 12:00 in owner's local timezone (set in `.context`)

---

## Writing Good Reminder Messages

The message fires hours or days later with no context. Write it like a friend texting you:

❌ `"Reminder: follow up on Redis board"`
✅ `"Hey — time to follow up with the cvms team on the Redis migration. Check if cleanup is done."`

Keep it short, human, and self-contained.

---

## Listing Reminders

```bash
cat data/reminders.json | jq '.[] | {id, datetime, message}'
```

## Removing a Reminder

```bash
# Remove by ID using jq
jq 'map(select(.id != "call-mom-apr7"))' data/reminders.json > /tmp/r.json && mv /tmp/r.json data/reminders.json
```

Or just open the file and delete the entry — it's plain JSON.

---

## Credit

Built by Janet (Gabriel Amram's PA) — April 2026.
Inspired by `quick-reminders` by Heleni. Solves the reboot-survival gap for long-dated reminders.
