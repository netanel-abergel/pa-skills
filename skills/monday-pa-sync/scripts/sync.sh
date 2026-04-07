#!/usr/bin/env bash
# monday-pa-sync/scripts/sync.sh
# Syncs open monday.com board items to today's PA memory file
# Usage: ./sync.sh [--board-id BOARD_ID] [--out-dir MEMORY_DIR]
# Deps: curl, jq

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONTEXT_FILE="$SKILL_DIR/.context"

if [[ -f "$CONTEXT_FILE" ]]; then
  set -a; source "$CONTEXT_FILE"; set +a
fi

MONDAY_API_TOKEN="${MONDAY_API_TOKEN:-$(cat ~/.credentials/monday-token.txt 2>/dev/null || echo "")}"
MONDAY_BOARD_ID="${MONDAY_BOARD_ID:-}"
MEMORY_DIR="${MEMORY_DIR:-$HOME/workspace/memory}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --board-id) MONDAY_BOARD_ID="$2"; shift 2 ;;
    --out-dir)  MEMORY_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$MONDAY_API_TOKEN" ]]; then
  echo "Error: MONDAY_API_TOKEN not set." >&2; exit 1
fi
if [[ -z "$MONDAY_BOARD_ID" ]]; then
  echo "Error: MONDAY_BOARD_ID not set." >&2; exit 1
fi

TODAY=$(date +%Y-%m-%d)
NOW=$(date +%H:%M)
MEMORY_FILE="$MEMORY_DIR/$TODAY.md"
mkdir -p "$MEMORY_DIR"

QUERY="{\"query\":\"{ boards(ids: $MONDAY_BOARD_ID) { items_page(limit: 50) { items { id name column_values(ids: [\\\"status\\\", \\\"date4\\\"]) { text } } } } }\"}"

RESPONSE=$(curl -sf \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$QUERY" \
  https://api.monday.com/v2) || {
  echo "Error: monday.com API request failed" >&2; exit 1
}

ITEMS=$(echo "$RESPONSE" | jq -r '
  .data.boards[0].items_page.items[] |
  "- [ ] \(.name) — [\(.column_values[0].text // "no status")] — due: \(.column_values[1].text // "—")"
' 2>/dev/null) || ITEMS="(no open items)"

if [[ -f "$MEMORY_FILE" ]]; then
  TEMP=$(mktemp)
  awk '/^## Monday Tasks \(synced/{skip=1} /^## / && !/^## Monday Tasks/{skip=0} !skip{print}' "$MEMORY_FILE" > "$TEMP"
  mv "$TEMP" "$MEMORY_FILE"
fi

{ echo ""; echo "## Monday Tasks (synced $NOW)"; echo "$ITEMS"; } >> "$MEMORY_FILE"
echo "✅ monday-pa-sync: wrote tasks to $MEMORY_FILE"
