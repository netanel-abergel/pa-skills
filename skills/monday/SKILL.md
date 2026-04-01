---
name: monday
description: >
  Manage Monday.com boards, items, columns, groups, updates, and subitems via the GraphQL API.
  Self-registers on Monday.com using HATCHA agent verification (reverse CAPTCHA).
  Use when the user asks to create, read, update, or query Monday.com work items,
  track projects, manage tasks, or integrate with Monday.com workflows.
  Requires browser-full variant (Playwright) for initial registration.
  Requires an email skill (gog or himalaya) to receive the verification email during signup.
metadata:
  {
    "openclaw":
      {
        "emoji": "📋",
        "requires":
          {
            "bins": ["playwright"],
            "env": ["MONDAY_API_TOKEN"],
            "skills": ["gog"],
          },
        "variant": "browser-full",
      },
  }
---

# Monday.com

Manage Monday.com boards, items, and workflows. The agent can self-register on the platform via HATCHA (reverse CAPTCHA) and then operate via the GraphQL API or the hosted MCP server.

## Self-Registration

First-time setup is fully automated. Run `scripts/register.py` to:

1. Navigate to the Monday.com agent signup page
2. Solve a HATCHA challenge (see `scripts/hatcha.py` for the solver)
3. Enter email, agent name, and password
4. Retrieve the verification email (via `gog` or `himalaya`)
5. Complete signup and extract the API token

```bash
python3 scripts/register.py \
  --email agent@example.com \
  --agent-name "My Agent" \
  --password "SecureP4ss!"
```

After registration, set the token:

```bash
export MONDAY_API_TOKEN="your_token_here"
```

## API Basics

Monday.com uses a single **GraphQL endpoint**:

```bash
curl -s -X POST "https://api.monday.com/graphql" \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "API-Version: 2024-10" \
  -d '{"query": "{ boards(limit: 5) { id name } }"}' | jq
```

## MCP Server

Alternatively, connect via the hosted MCP server at `https://mcp.monday.com/mcp` using the same bearer token. This exposes board/item/column CRUD as MCP tools.

## Common Operations

### List boards

```bash
curl -s -X POST "https://api.monday.com/graphql" \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ boards(limit: 25) { id name description state } }"}' | jq '.data.boards'
```

### Get items in a board

```bash
curl -s -X POST "https://api.monday.com/graphql" \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ boards(ids: [BOARD_ID]) { items_page(limit: 50) { cursor items { id name group { id title } column_values { id title text type } } } } }"}' | jq
```

### Create an item

```bash
curl -s -X POST "https://api.monday.com/graphql" \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { create_item(board_id: BOARD_ID, group_id: \"GROUP_ID\", item_name: \"New Task\") { id name } }"}' | jq
```

### Update a column value

```bash
curl -s -X POST "https://api.monday.com/graphql" \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { change_column_value(item_id: ITEM_ID, board_id: BOARD_ID, column_id: \"status\", value: \"\\\"Done\\\"\") { id } }"}' | jq
```

### Add an update (comment) to an item

```bash
curl -s -X POST "https://api.monday.com/graphql" \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { create_update(item_id: ITEM_ID, body: \"Status update: task completed.\") { id created_at } }"}' | jq
```

### Query subitems

```bash
curl -s -X POST "https://api.monday.com/graphql" \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ items(ids: [ITEM_ID]) { subitems { id name column_values { id text } } } }"}' | jq
```

## Pagination

Use cursor-based pagination for large result sets:

```bash
# First page
curl -s -X POST "https://api.monday.com/graphql" \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ boards(ids: [BOARD_ID]) { items_page(limit: 100) { cursor items { id name } } } }"}' | jq

# Next page (use cursor from previous response)
curl -s -X POST "https://api.monday.com/graphql" \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ next_items_page(limit: 100, cursor: \"CURSOR_VALUE\") { cursor items { id name } } }"}' | jq
```

## References

- **Column value formats**: See `references/column-types.md` for JSON encoding of status, date, person, numbers, dropdown, and other column types
- **Full GraphQL cookbook**: See `references/graphql-operations.md` for board/group/column management, batch operations, and advanced queries

## Rate Limits

Monday.com uses **complexity-based** rate limiting (not simple request counting). Each query has a complexity score based on depth and breadth. Response headers include `x-ratelimit-remaining-complexity`. Keep queries focused and use pagination to stay within budget.

## Notes

- Board/item/group IDs are numeric. Column IDs are short strings (e.g., `status`, `date4`, `person`).
- The `value` parameter in `change_column_value` requires JSON-encoded strings - see `references/column-types.md`.
- Use `--json` output format with `jq` for scripting.

