#!/bin/bash
# check-reminders.sh — fires reminders whose datetime falls within the last 15 minutes
#
# Setup:
#   chmod +x scripts/check-reminders.sh
#   Add to crontab: */15 * * * * /path/to/this/script >> /path/to/logs/reminders.log 2>&1
#
# Reminder datetime format: ISO-8601 in owner's LOCAL timezone (e.g. "2026-04-20T10:00:00")
# Default time when not specified: 12:00 local time

# Load .context if present (for TIMEZONE and REMINDERS_JSON overrides)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_FILE="$SCRIPT_DIR/../.context"
if [ -f "$CONTEXT_FILE" ]; then
  source "$CONTEXT_FILE"
fi

TIMEZONE="${TIMEZONE:-Asia/Jerusalem}"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/opt/ocana/openclaw/workspace}"
REMINDERS_FILE="${REMINDERS_JSON:-$WORKSPACE_ROOT/data/reminders.json}"

if [ ! -f "$REMINDERS_FILE" ]; then
  echo "No reminders file found at $REMINDERS_FILE"
  exit 0
fi

# Current time and 15 minutes ago, in owner's timezone, as epoch seconds
NOW_EPOCH=$(TZ="$TIMEZONE" date +%s)
WINDOW_START=$((NOW_EPOCH - 15 * 60))

echo "Checking reminders between $(TZ="$TIMEZONE" date -d @$WINDOW_START '+%Y-%m-%dT%H:%M') and $(TZ="$TIMEZONE" date -d @$NOW_EPOCH '+%Y-%m-%dT%H:%M') ($TIMEZONE)"

# Loop through all reminders
jq -c '.[]' "$REMINDERS_FILE" | while IFS= read -r reminder; do
  ID=$(echo "$reminder" | jq -r '.id')
  DATETIME=$(echo "$reminder" | jq -r '.datetime')
  TARGET=$(echo "$reminder" | jq -r '.target')
  CHANNEL=$(echo "$reminder" | jq -r '.channel')
  MESSAGE=$(echo "$reminder" | jq -r '.message')

  # Convert reminder datetime (local TZ) to epoch
  REMINDER_EPOCH=$(TZ="$TIMEZONE" date -d "$DATETIME" +%s 2>/dev/null)
  if [ -z "$REMINDER_EPOCH" ]; then
    echo "Skipping $ID — could not parse datetime: $DATETIME"
    continue
  fi

  # Fire if reminder falls within the 15-minute window
  if [ "$REMINDER_EPOCH" -gt "$WINDOW_START" ] && [ "$REMINDER_EPOCH" -le "$NOW_EPOCH" ]; then
    echo "Firing reminder: $ID ($DATETIME) → $TARGET via $CHANNEL"
    openclaw message send --channel "$CHANNEL" --target "$TARGET" --message "$MESSAGE"
  fi
done
