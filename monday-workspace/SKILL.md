---
name: monday-workspace
description: "Set up a monday.com account for an OpenClaw agent and work with monday.com boards, items, and updates via the GraphQL API or MCP server. Use when: creating a monday.com workspace for a PA, connecting the PA to monday.com, querying boards and items, creating or updating items, or troubleshooting monday.com API access. Covers account creation, token setup, GraphQL operations, and MCP configuration. Works with any LLM model."
---

# monday.com Workspace Skill

## Minimum Model
Any model for routine operations. Use a medium model for debugging GraphQL errors.

---

## Part 1 — Account Setup

### Create a monday.com Account for a PA

Each PA needs its own account — do not use the owner's.

1. Go to [monday.com/agents-signup](https://monday.com/agents-signup).
2. Use the agent email (e.g. `agent@agentdomain.com`).
3. Owner invites the PA via Admin → Users → Invite.

### Get an API Token

1. Log into monday.com as the agent.
2. Click avatar → **Developers** → **My Access Tokens** → **Copy**.
3. Save the token:

```bash
# Create secure credentials directory
mkdir -p ~/.credentials
chmod 700 ~/.credentials

# Save token to file with restricted permissions
echo "TOKEN_HERE" > ~/.credentials/monday-token.txt
chmod 600 ~/.credentials/monday-token.txt

# Load token into environment
export MONDAY_API_TOKEN=$(cat ~/.credentials/monday-token.txt)

# Make it permanent across sessions
echo 'export MONDAY_API_TOKEN=$(cat ~/.credentials/monday-token.txt)' >> ~/.bashrc
```

---

## Part 2 — API Usage (GraphQL)

### Setup

```bash
MONDAY_API_URL="https://api.monday.com/v2"

# Load token from env or file
if [ -z "$MONDAY_API_TOKEN" ]; then
  MONDAY_API_TOKEN=$(cat ~/.credentials/monday-token.txt 2>/dev/null)
fi

if [ -z "$MONDAY_API_TOKEN" ]; then
  echo "ERROR: MONDAY_API_TOKEN not set and ~/.credentials/monday-token.txt not found"
  exit 1
fi

# Reusable helper function for all API calls
monday_query() {
  RESPONSE=$(curl -s -X POST "$MONDAY_API_URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: $MONDAY_API_TOKEN" \
    -H "API-Version: 2024-01" \
    -d "$1")

  # Print response or error
  if echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('errors'):
    print('API ERROR:', d['errors'])
    sys.exit(1)
" 2>/dev/null; then
    echo "$RESPONSE"
  else
    echo "API ERROR: $RESPONSE" >&2
    return 1
  fi
}
```

### Common Operations

```bash
# List all boards (up to 20)
monday_query '{"query": "{ boards(limit: 20) { id name } }"}'

# Get items from a board
monday_query '{"query": "{ boards(ids: [BOARD_ID]) { items_page { items { id name state } } } }"}'

# Create an item
monday_query '{
  "query": "mutation ($board: ID!, $name: String!) { create_item(board_id: $board, item_name: $name) { id } }",
  "variables": {"board": "BOARD_ID", "name": "New Item Name"}
}'

# Update a status column
monday_query '{
  "query": "mutation ($board: ID!, $item: ID!, $col: String!, $val: JSON!) { change_column_value(board_id: $board, item_id: $item, column_id: $col, value: $val) { id } }",
  "variables": {
    "board": "BOARD_ID",
    "item": "ITEM_ID",
    "col": "status",
    "val": "{\"label\": \"Done\"}"
  }
}'

# Add a comment to an item
monday_query '{
  "query": "mutation ($item: ID!, $body: String!) { create_update(item_id: $item, body: $body) { id } }",
  "variables": {"item": "ITEM_ID", "body": "Update text here"}
}'

# List columns in a board
monday_query '{"query": "{ boards(ids: [BOARD_ID]) { columns { id title type } } }"}'

# Get current user info
monday_query '{"query": "{ me { id name email account { id name } } }"}'
```

### Pagination for Large Boards

```bash
# First page — also returns a cursor for the next page
monday_query '{"query": "{ boards(ids: [BOARD_ID]) { items_page(limit: 50) { cursor items { id name } } } }"}'

# Next page — pass the cursor value from the previous response
monday_query '{"query": "{ next_items_page(limit: 50, cursor: \"CURSOR_VALUE\") { cursor items { id name } } }"}'
```

### Check Before Creating (Avoid Duplicates)

```bash
# Search for item by name before creating
RESULT=$(monday_query '{"query": "{ items_by_multiple_column_values(board_id: BOARD_ID, column_id: \"name\", column_values: [\"Item Name\"]) { id name } }"}')

# Count how many items matched
COUNT=$(echo "$RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(len(d.get('data', {}).get('items_by_multiple_column_values', [])))
")

# Create only if it doesn't exist
if [ "$COUNT" -eq 0 ]; then
  echo "Item not found — creating it"
  # proceed with create
else
  echo "Item already exists — skipping"
fi
```

### Batch Update Multiple Items

```bash
# Loop through item IDs with a small delay to respect rate limits
for ITEM_ID in 123456 789012 345678; do
  monday_query "{
    \"query\": \"mutation { change_column_value(board_id: BOARD_ID, item_id: $ITEM_ID, column_id: \\\"status\\\", value: \\\"{\\\\\\\"label\\\\\\\": \\\\\\\"In Progress\\\\\\\"}\\\") { id } }\"
  }"
  # Pause 200ms between calls to stay under rate limits
  sleep 0.2
done
```

---

## Part 3 — MCP Server (Recommended)

The monday.com MCP server lets you work with boards using natural language — no manual GraphQL needed.

### Option A: Hosted MCP

Add to `~/.openclaw/openclaw.json` under `mcpServers`:

```json
{
  "mcpServers": {
    "monday-mcp": {
      "url": "https://mcp.monday.com/mcp"
    }
  }
}
```

No local install needed. Uses OAuth.

Test it:
```bash
mcporter call monday-mcp list_boards
```

### Option B: Local MCP (npx)

```json
{
  "mcpServers": {
    "monday-api-mcp": {
      "command": "npx",
      "args": ["@mondaydotcomorg/monday-api-mcp@latest"],
      "env": {
        "MONDAY_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

If `npx` is slow:
```bash
# Install globally to avoid cold starts
npm install -g @mondaydotcomorg/monday-api-mcp
# Then use "command": "monday-api-mcp" in the config above
```

---

## Part 4 — Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| 401 Unauthorized | Token invalid or expired | Regenerate token in Developer settings, update file |
| 403 Forbidden | No board access | Ask owner to share the board with the PA account |
| "Column not found" | Wrong column ID | Run `list columns` query first |
| "Complexity budget exhausted" | Query too heavy | Use pagination with `limit: 50` |
| Empty response | Network or JSON issue | Run `echo $RESPONSE | python3 -m json.tool` to inspect |
| Rate limit (429) | >5000 requests/min | Add `sleep 0.2` between calls in loops |

---

## Part 5 — Setup Checklist

```
[ ] PA has a monday.com account (agent email, not owner's)
[ ] API token saved to ~/.credentials/monday-token.txt
[ ] MONDAY_API_TOKEN exported in shell
[ ] Workspace access confirmed
[ ] Verified with: monday_query '{"query": "{ me { id name } }"}'
[ ] If using MCP: server added to config and tested
```

**Rules:**
- Do NOT create or update board items without explicit instruction from owner.
- Always confirm board ID before mutations.
- Never print or log the API token.

---

## Cost Tips

- **Cheap:** The MCP server handles natural language → API translation. Use it to avoid writing complex GraphQL.
- **Expensive:** Fetching all items from large boards without pagination. Always use `limit:`.
- **Batch:** Use a loop with `sleep 0.2` for bulk updates — not one API call per session.
- **Small model OK:** Routine operations (list, create, update) work with any model.
- **Use medium model for:** Debugging GraphQL errors or constructing complex queries.
