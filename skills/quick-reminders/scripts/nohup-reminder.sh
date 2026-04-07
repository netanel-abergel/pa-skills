#!/usr/bin/env bash
# nohup-reminder.sh — zero-LLM one-shot reminders for OpenClaw PAs
# Usage:
#   add "message text" --target <jid/phone> -t TIME [-z TIMEZONE] [--channel whatsapp|telegram]
#   list
#   remove ID [ID ...]
#   remove --all

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
REMINDERS_JSON="${REMINDERS_JSON:-$WORKSPACE_DIR/data/reminders.json}"

mkdir -p "$(dirname "$REMINDERS_JSON")"
[ -f "$REMINDERS_JSON" ] || echo "[]" > "$REMINDERS_JSON"

_now_epoch() { date +%s; }
_iso() { date -d "@$1" --iso-8601=seconds 2>/dev/null || date -r "$1" +"%Y-%m-%dT%H:%M:%S%z"; }

_parse_time() {
  local raw="$1" tz="$2"
  # Relative: 2h, 30m, 90s
  if [[ "$raw" =~ ^([0-9]+)(h|m|s)$ ]]; then
    local n="${BASH_REMATCH[1]}" u="${BASH_REMATCH[2]}"
    local delta=0
    case "$u" in h) delta=$((n*3600));; m) delta=$((n*60));; s) delta=$n;; esac
    echo $(( $(_now_epoch) + delta ))
    return
  fi
  # Absolute: parse with optional timezone
  if [ -n "$tz" ]; then
    TZ="$tz" date -d "$raw" +%s 2>/dev/null || TZ="$tz" date -j -f "%H:%M" "$raw" +%s 2>/dev/null
  else
    date -d "$raw" +%s 2>/dev/null || date -j -f "%H:%M" "$raw" +%s 2>/dev/null
  fi
}

_gen_id() {
  echo "reminder-$(date +%s)-$RANDOM"
}

cmd_add() {
  local message="" target="" time_raw="" timezone="" channel="whatsapp"

  # Parse args
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --target|-T) target="$2"; shift 2;;
      -t|--time)   time_raw="$2"; shift 2;;
      -z|--tz)     timezone="$2"; shift 2;;
      --channel|-c) channel="$2"; shift 2;;
      *) message="$1"; shift;;
    esac
  done

  [ -z "$message" ] && { echo "Error: message required"; exit 1; }
  [ -z "$target" ]  && { echo "Error: --target required"; exit 1; }
  [ -z "$time_raw" ] && { echo "Error: -t TIME required"; exit 1; }

  local epoch
  epoch=$(_parse_time "$time_raw" "$timezone")
  [ -z "$epoch" ] && { echo "Error: could not parse time '$time_raw'"; exit 1; }

  local now; now=$(_now_epoch)
  local delta=$(( epoch - now ))
  [ "$delta" -le 0 ] && { echo "Error: time is in the past"; exit 1; }

  local id; id=$(_gen_id)
  local fires_at; fires_at=$(_iso "$epoch")

  # Add to JSON
  local entry
  entry=$(printf '{"id":"%s","message":"%s","target":"%s","channel":"%s","fires_epoch":%d,"fires_at":"%s"}' \
    "$id" "$message" "$target" "$channel" "$epoch" "$fires_at")

  local tmp; tmp=$(mktemp)
  python3 -c "
import json, sys
data = json.load(open('$REMINDERS_JSON'))
data.append(json.loads(sys.stdin.read()))
json.dump(data, open('$REMINDERS_JSON','w'), indent=2)
" <<< "$entry"

  # Fire in background
  (
    sleep "$delta"
    openclaw message send --channel "$channel" --to "$target" --message "$message"
    # Remove from JSON after firing
    python3 -c "
import json
data = json.load(open('$REMINDERS_JSON'))
data = [r for r in data if r['id'] != '$id']
json.dump(data, open('$REMINDERS_JSON','w'), indent=2)
"
  ) &
  disown

  echo "✅ Reminder set: '$message' → $fires_at (id: $id)"
}

cmd_list() {
  local now; now=$(_now_epoch)
  python3 -c "
import json, sys
data = json.load(open('$REMINDERS_JSON'))
if not data:
    print('No pending reminders.')
    sys.exit(0)
for r in data:
    delta = r.get('fires_epoch', 0) - $now
    if delta > 0:
        h, m = divmod(delta // 60, 60)
        eta = f'{h}h {m}m' if h else f'{m}m'
    else:
        eta = 'overdue'
    print(f\"[{r['id']}] {r['fires_at']} (+{eta}) → {r['channel']}:{r['target']}: {r['message']}\")
"
}

cmd_remove() {
  if [ "$1" = "--all" ]; then
    echo "[]" > "$REMINDERS_JSON"
    echo "All reminders removed."
    return
  fi
  local ids=("$@")
  python3 -c "
import json
ids = $(printf '"%s",' "${ids[@]}" | sed 's/,$//' | xargs -I{} echo '[{}]')
data = json.load(open('$REMINDERS_JSON'))
removed = [r for r in data if r['id'] in ids]
data = [r for r in data if r['id'] not in ids]
json.dump(data, open('$REMINDERS_JSON','w'), indent=2)
print(f'Removed {len(removed)} reminder(s).')
"
}

CMD="${1:-help}"
shift || true

case "$CMD" in
  add)    cmd_add "$@";;
  list)   cmd_list;;
  remove) cmd_remove "$@";;
  *)
    echo "Usage: nohup-reminder.sh <add|list|remove> [options]"
    echo "  add \"message\" --target <id> -t TIME [-z TZ] [--channel whatsapp|telegram]"
    echo "  list"
    echo "  remove ID [ID ...]  |  remove --all"
    ;;
esac
