---
name: monday-workspace
description: Set up a monday.com account for an OpenClaw agent and work with monday.com boards, items, and updates via the GraphQL API. Use when someone needs to create a monday.com workspace for their PA, connect the PA to monday.com, query boards/items, create or update items, or troubleshoot monday API access. Covers account creation, token setup, and common GraphQL operations.
---

# monday.com Workspace Skill

Use this skill to set up and operate monday.com from an OpenClaw agent.

---

## Part 1 — Account Setup

### Creating a monday.com Account for a PA

Each PA should have its **own monday.com account** (not the owner's).

⚠️ **Use the dedicated agents signup URL:**
👉 [monday.com/agents-signup](https://monday.com/agents-signup)

Recommended flow:
1. Go to [monday.com/agents-signup](https://monday.com/agents-signup)
2. Use the agent email (e.g. `midgee@openclaw.ai` or a dedicated PA email)
3. Create or join a workspace — the owner can invite the PA to their workspace
4. Once logged in, generate an API token (see below)

### Getting an API Token

1. In monday.com → click avatar (top right) → **Developers**
2. Go to **My Access Tokens**
3. Copy the personal API token
4. Save it securely — store in `/root/.credentials/monday-<name>-token.txt`
5. Export in shell: `export MONDAY_API_TOKEN=$(cat /root/.credentials/monday-<name>-token.txt)`
6. Add to `~/.bashrc` for persistence: `echo 'export MONDAY_API_TOKEN=...' >> ~/.bashrc`

### Connecting to a Workspace

If the owner wants to give the PA access to their workspace:
- Owner goes to monday.com → **Admin** → **Users** → **Invite Members**
- Invites the PA email with appropriate role (Member or Viewer)
- PA accepts invite, then generates token from their own account

---

## Part 2 — API Usage (GraphQL)

### Base Setup

```bash
MONDAY_API_TOKEN="your_token_here"
MONDAY_API_URL="https://api.monday.com/v2"

monday_query() {
  curl -s -X POST "$MONDAY_API_URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: $MONDAY_API_TOKEN" \
    -H "API-Version: 2024-01" \
    -d "$1"
}
```

### Common Operations

#### List boards
```bash
monday_query '{"query": "{ boards(limit: 20) { id name description } }"}'
```

#### Get items from a board
```bash
monday_query '{"query": "{ boards(ids: [BOARD_ID]) { items_page { items { id name state } } } }"}'
```

#### Create an item
```bash
monday_query '{
  "query": "mutation ($board: ID!, $name: String!) { create_item(board_id: $board, item_name: $name) { id } }",
  "variables": {"board": "BOARD_ID", "name": "New Item Name"}
}'
```

#### Update an item column
```bash
monday_query '{
  "query": "mutation ($board: ID!, $item: ID!, $col: String!, $val: JSON!) { change_column_value(board_id: $board, item_id: $item, column_id: $col, value: $val) { id } }",
  "variables": {"board": "BOARD_ID", "item": "ITEM_ID", "col": "status", "val": "{\"label\": \"Done\"}"}
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
monday_query '{
  "query": "{ items_by_multiple_column_values(board_id: BOARD_ID, column_id: \"name\", column_values: [\"search term\"]) { id name } }"
}'
```

#### Get account/workspace info
```bash
monday_query '{"query": "{ me { id name email account { id name } } }"}'
```

---

## Part 3 — Credentials Reference

Standard locations:
- Token file: `/root/.credentials/monday-<workspace>-token.txt`
- Env var: `MONDAY_API_TOKEN`
- Workspace ID: stored in `MEMORY.md` or `TOOLS.md` under monday.com section

For Heleni specifically:
- Workspace: your OpenClaw workspace ID (configure in MEMORY.md or TOOLS.md)
- Account: `heleni@openclaw.ai`
- PA Rollout Board ID: `18405314499`

---

## Part 4 — Troubleshooting

**401 Unauthorized** → Token expired or wrong. Regenerate from monday.com Developer settings.

**403 Forbidden** → Account doesn't have access to that board. Check workspace membership and board permissions.

**"Column not found"** → Column ID is wrong. Use this to list columns:
```bash
monday_query '{"query": "{ boards(ids: [BOARD_ID]) { columns { id title type } } }"}'
```

**Rate limits** → monday.com API allows ~5,000 requests/minute on most plans. If hitting limits, add delays between calls.

**API version issues** → Always include `"API-Version": "2024-01"` header to avoid breaking changes.

---

## Part 5 — monday.com MCP Server

The official monday.com MCP server lets OpenClaw agents interact with monday.com through the Model Context Protocol — no need to hand-craft GraphQL queries.

### Option A: Hosted MCP (Recommended — easiest)

Add to OpenClaw MCP config (`~/.openclaw/openclaw.json` under `tools.mcp.servers`):

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
- Auto-updates, enterprise uptime
- Works immediately

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

Install manually if needed:
```bash
npm install -g @mondaydotcomorg/monday-api-mcp
```

### Option C: Remote hosted (with API version header)

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

Once connected, the agent can:
- Read and search boards, items, groups, columns
- Create items, subitems, updates
- Change column values and statuses
- Query workspaces and users
- Manage work forms

### Testing the MCP Connection

After setup, test with a simple prompt to the agent:
> "List my monday.com boards"

Or verify via mcporter:
```bash
mcporter call monday-mcp boards
```

### Troubleshooting MCP

**Auth error** → Re-authenticate via OAuth or verify `MONDAY_API_TOKEN` is set correctly
**Server not found** → Confirm MCP server config is under the correct key in openclaw.json
**npx timeout** → Try `npm install -g @mondaydotcomorg/monday-api-mcp` first, then use `monday-api-mcp` as command instead of npx

---

## Part 6 — Integration with OpenClaw

When helping a PA get started with monday.com:
1. Confirm the PA has a monday.com account (agent email, not owner's)
2. Confirm the token is saved and exported
3. Confirm workspace access (invited by owner if needed)
4. Test GraphQL with: `monday_query '{"query": "{ me { id name } }"}'`
5. If using MCP: configure the server and test with a natural language query
6. Only then proceed to board operations

Do NOT create items or update boards on behalf of the owner without explicit instruction.
Always confirm board ID before making mutations.
