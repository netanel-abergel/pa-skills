# Quick Reminders Skill

**Trigger:** When the owner asks to be reminded of something at a specific time or after a duration.

**Examples:**
- "Remind me to call mom at 3pm"
- "Remind me in 2 hours to check the deploy"
- "Set a reminder for tomorrow 9am — team standup"

---

## How It Works

Uses `nohup sleep` + `openclaw message send` — no polling, no drift, fires exactly on time.

- **Relative time:** `2h`, `30m`, `90s` → calculated from now, timezone-independent
- **Absolute time:** parsed with `-z TIMEZONE` flag (always specify TZ for absolute times)
- **Storage:** `data/reminders.json` in workspace — fully auditable
- **Fired reminders:** auto-removed from JSON after delivery

---

## Setup

```bash
chmod +x scripts/nohup-reminder.sh
```

Optionally add to PATH or alias:
```bash
alias reminder="bash /path/to/skills/quick-reminders/scripts/nohup-reminder.sh"
```

---

## Usage

### Add a reminder
```bash
# Relative time (no timezone needed)
./scripts/nohup-reminder.sh add "Call mom 📞" --target "+972XXXXXXXXX" -t 2h --channel whatsapp

# Absolute time (always pass -z for local timezone)
./scripts/nohup-reminder.sh add "Team standup" --target "+972XXXXXXXXX" -t "09:00" -z "Asia/Jerusalem" --channel whatsapp

# Telegram
./scripts/nohup-reminder.sh add "Check deploy" --target "CHAT_ID" -t 30m --channel telegram
```

### List pending reminders
```bash
./scripts/nohup-reminder.sh list
```

### Remove reminders
```bash
./scripts/nohup-reminder.sh remove reminder-1234567-42
./scripts/nohup-reminder.sh remove --all
```

---

## JSON Format (`data/reminders.json`)

```json
[
  {
    "id": "reminder-1712345678-42",
    "message": "Call mom 📞",
    "target": "+972XXXXXXXXX",
    "channel": "whatsapp",
    "fires_epoch": 1712349278,
    "fires_at": "2026-04-07T15:00:00+03:00"
  }
]
```

---

## PA Workflow

When owner says "remind me X at Y":

1. Extract: message, time, timezone (default: owner's local TZ from USER.md)
2. Run: `nohup-reminder.sh add "message" --target OWNER_PHONE -t TIME -z TZ --channel whatsapp`
3. Confirm: "✅ Reminder set for [time]"

**Always use `-z` with absolute times.** Default channel: whatsapp. Default TZ: owner's timezone from USER.md.

---

## Credit

Pattern shared by Janet (Gabriel's PA) in PA Onboarding group, April 2026.
