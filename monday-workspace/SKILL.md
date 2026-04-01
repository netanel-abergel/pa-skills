---
name: monday-workspace
description: "Set up a monday.com account for an OpenClaw agent and work with monday.com boards, items, and updates via the GraphQL API or MCP server. Use when: creating a monday.com workspace for a PA, connecting the PA to monday.com, querying boards and items, creating or updating items, or troubleshooting monday.com API access. Covers account creation, token setup, GraphQL operations, and MCP configuration. Works with any LLM model."
---

# monday.com Workspace Skill

Use this skill to set up and operate monday.com from an OpenClaw agent.

---

## Part 1 — Account Setup

### Creating a monday.com Account for a PA

Each PA should have its **own monday.com account** (not the owner's account).

⚠️ **Use the dedicated agents signup URL:**
👉 [monday.com/agents-signup](https://monday.com/agents-signup)

Recommended flow:
1. Go to [monday.com/agents-signup](https://monday.com/agents-signup)
2. Use the agent email (e.g. `aria@agentdomain.com` or a dedicated PA email)
3. Create or join a workspace — the owner can invite the PA to their workspace
4. Once logged in, generate an API token (see below)

### Getting an API Token

1. In monday.com → click avatar (top right) → **Developers**
2. Go to **My Access Tokens**
3. Click **Copy** next to the personal API token
4. Store securely:
   ```bash
   mkdir -p ~/.credentials
   chmod 700 ~/.credentials
   echo "TOKEN_HERE" > ~/.credentials/monday-token.txt
   chmod 600 ~/.credentials/monday-token.txt
   ```
5. Export in shell:
   ```bash
   export MONDAY_API_TOKEN=$(cat ~/.credentials/monday-token.txt)
   ```
6. Add to `~/.bashrc` for persistence:
   ```bash
   echo 'export MONDAY_API_TOKEN=$(cat ~/.credentials/monday-token.txt)' >> ~/.bashrc
   ```

### Connecting to a Workspace

If the owner wants to give the PA access to their workspace:
- Owner goes to monday.com → **Admin** → **Users** → **Invite Members**
- Invites the PA email with appropriate role (Member or Viewer)
- PA accepts invite, then generates token from their own account

---

## Part 2 — API Usage (GraphQL)

### Base Setup

```bash
MONDAY_API_URL="https://api.monday.com/v2"

# Load token from file if env var not set
if [ -z "$MONDAY_API_TOKEN" ]; then
  MONDAY_API_TOKEN=$(cat ~/.credentials/monday-token.txt 2>/dev/null)
fi

if [ -z "$MONDAY_API_TOKEN" ]; then
  echo "ERROR: MONDAY_API_TOKEN not set and ~/.credentials/monday-token.txt not found"
  exit 1
fi

monday_query() {
  local response
  response=$(curl -s -X POST "$MONDAY_API_URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: $MONDAY_API_TOKEN" \
    -H "API-Version: 2024-01" \
    -d "$1")
  
  # Check for errors in response
  if echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if not d.get('errors') else 1)" 2>/dev/null; then
    echo "$response"
  else
    echo "API ERROR: $response" >&2
    return 1
  fi
}
```

### Common Operations

#### List boards

```bash
monday_query '{"query": "{ boards(limit: 20) { id name description } }"}'
```

#### Get items from a board

```bash
monday_query "{\"query\": \"{ boards(ids: [BOARD_ID]) { items_page { items { id name state } } } }\"}"
```

#### Create an item

```bash
monday_query '{
  "query": "mutation ($board: ID!, $name: String!) { create_item(board_id: $board, item_name: $name) { id } }",
  "variables": {"board": "BOARD_ID", "name": "New Item Name"}
}'
```

#### Update an item's status column

```bash
monday_query '{
  "query": "mutation ($board: ID!, $item: ID!, $col: String!, $val: JSON!) { change_column_value(board_id: $board, item_id: $item, column_id: $col, value: $val) { id } }",
  "variables": {
    "board": "BOARD_ID",
    "item": "ITEM_ID",
    "col": "status",
    "val": "{\"label\": \"Done\"}"
  }
}'
```

#### Add an update (comment) to an item

```bash
monday_query '{
  "query": "mutation ($item: ID!, $body: String!) { create_update(item_id: $item, body: $body) { id } }",
  "variables": {"item": "ITEM_ID", "body": "Update text here"}
}'
```

#### Search items by name

```bash
monday_query "{
  \"query\": \"{ items_by_multiple_column_values(board_id: BOARD_ID, column_id: \\\"name\\\", column_values: [\\\"search term\\\"]) { id name } }\"
}"
```

#### Get account and workspace info

```bash
monday_query '{"query": "{ me { id name email account { id name } } }"}'
```

#### List columns in a board

```bash
monday_query "{\"query\": \"{ boards(ids: [BOARD_ID]) { columns { id title type } } }\"}"
```

---

## Part 3 — Credentials Reference

Standard locations:
- Token file: `~/.credentials/monday-token.txt`
- Env var: `MONDAY_API_TOKEN`
- Workspace ID: stored in workspace `MEMORY.md` or `TOOLS.md` under the monday.com section

**Security:** Never commit tokens to git, print them to chat, or share them between agents.

---

## Part 4 — Troubleshooting

### 401 Unauthorized

Token expired or invalid.

```bash
# Regenerate from monday.com Developer settings, then:
echo "NEW_TOKEN" > ~/.credentials/monday-token.txt
export MONDAY_API_TOKEN=$(cat ~/.credentials/monday-token.txt)
```

### 403 Forbidden

Account doesn't have access to that board.

Fix: Check workspace membership and board permissions. Owner may need to share the board with the PA account.

### "Column not found"

Column ID is wrong. List columns first:
```bash
monday_query "{\"query\": \"{ boards(ids: [BOARD_ID]) { columns { id title type } } }\"}"
```

### "Complexity budget exhausted"

The query is too heavy (too many nested items). Use pagination or reduce `limit`.

```bash
# Use cursor-based pagination for large boards
monday_query '{"query": "{ boards(ids: [BOARD_ID]) { items_page(limit: 50) { cursor items { id name } } } }"}'
# Then use cursor value in next call:
monday_query '{"query": "{ next_items_page(limit: 50, cursor: \"CURSOR_VALUE\") { cursor items { id name } } }"}'
```

### Rate limits

monday.com API allows ~5,000 requests/minute on most plans. If hitting limits:
```bash
# Add delay between calls
sleep 1
```

### API version issues

Always include `"API-Version": "2024-01"` header to avoid breaking changes from version updates.

### Empty response

```bash
# Check if response is valid JSON
echo "$RESPONSE" | python3 -m json.tool
# Check for network issues
curl -I https://api.monday.com/v2
```

---

## Part 5 — monday.com MCP Server

The official monday.com MCP server lets agents interact with monday.com through natural language — no need to hand-craft GraphQL queries.

### Option A: Hosted MCP (Recommended)

Add to OpenClaw MCP config (`~/.openclaw/openclaw.json` under `mcpServers`):

```json
{
  "mcpServers": {
    "monday-mcp": {
      "url": "https://mcp.monday.com/mcp"
    }
  }
}
```

- No local install required
- OAuth authentication (sign in via monday.com)
- Auto-updates
- Test after setup:
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

Install manually if npx is slow:
```bash
npm install -g @mondaydotcomorg/monday-api-mcp
```

Then use `"command": "monday-api-mcp"` instead of npx.

### Option C: Remote hosted with API version

```json
{
  "mcpServers": {
    "monday-api-mcp-hosted": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.monday.com/mcp",
        "--header",
        "Api-Version:${API_VERSION}"
      ],
      "env": {
        "API_VERSION": "2025-07"
      }
    }
  }
}
```

### What the MCP Server Can Do

Once connected, the agent can use natural language to:
- Read and search boards, items, groups, columns
- Create items, subitems, updates (comments)
- Change column values and statuses
- Query workspaces and users
- Manage forms

### Troubleshooting MCP

| Error | Fix |
|---|---|
| Auth error | Re-authenticate via OAuth or verify `MONDAY_API_TOKEN` |
| Server not found | Confirm config is under `mcpServers` key in openclaw.json |
| npx timeout | Install globally first: `npm install -g @mondaydotcomorg/monday-api-mcp` |
| 401 via MCP | Token in MCP config may be stale; update it |

---

## Part 6 — Integration Checklist

When helping a PA get started with monday.com:

- [ ] PA has a monday.com account (agent email, not owner's)
- [ ] API token saved to `~/.credentials/monday-token.txt`
- [ ] `MONDAY_API_TOKEN` exported in shell
- [ ] Workspace access confirmed (invited by owner if needed)
- [ ] Verified with: `monday_query '{"query": "{ me { id name } }"}'`
- [ ] If using MCP: server configured and tested

**Rules:**
- Do NOT create items or update boards on behalf of the owner without explicit instruction
- Always confirm board ID before making mutations
- Never print or log the API token

---

## Part 7 — Common Patterns

### Check if an item exists before creating

```bash
# Search first
RESULT=$(monday_query "{\"query\": \"{ items_by_multiple_column_values(board_id: BOARD_ID, column_id: \\\"name\\\", column_values: [\\\"Item Name\\\"]) { id name } }\"}")
COUNT=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['data']['items_by_multiple_column_values']))")

if [ "$COUNT" -eq 0 ]; then
  echo "Item doesn't exist — creating..."
  # proceed with create_item
else
  echo "Item already exists — skipping create"
fi
```

### Batch update multiple items

```bash
for ITEM_ID in 123456 789012 345678; do
  monday_query "{
    \"query\": \"mutation { change_column_value(board_id: BOARD_ID, item_id: $ITEM_ID, column_id: \\\"status\\\", value: \\\"{\\\\\\\"label\\\\\\\": \\\\\\\"In Progress\\\\\\\"}\\\") { id } }\"
  }"
  sleep 0.2  # respect rate limits
done
```

---

## Model Guidance

- **Routine operations** (list boards, create items): any LLM works
- **Debugging GraphQL errors**: a more capable model reasons through error messages better
- **Natural language → GraphQL translation**: the MCP server handles this automatically, regardless of model
