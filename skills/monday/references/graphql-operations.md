# Monday.com GraphQL Operations

All requests go to `https://api.monday.com/graphql` with header `Authorization: $MONDAY_API_TOKEN`.

## Boards

**Create a board:**

```graphql
mutation {
  create_board(board_name: "Project Alpha", board_kind: public) {
    id name
  }
}
```

**Get board with columns schema:**

```graphql
{
  boards(ids: [BOARD_ID]) {
    id name
    columns { id title type settings_str }
    groups { id title color }
  }
}
```

**Delete a board:**

```graphql
mutation {
  delete_board(board_id: BOARD_ID) { id }
}
```

## Groups

**Create a group:**

```graphql
mutation {
  create_group(board_id: BOARD_ID, group_name: "Sprint 3") {
    id title
  }
}
```

**Delete a group:**

```graphql
mutation {
  delete_group(board_id: BOARD_ID, group_id: "GROUP_ID") {
    id
  }
}
```

## Items

**Create item with column values:**

```graphql
mutation {
  create_item(
    board_id: BOARD_ID,
    group_id: "GROUP_ID",
    item_name: "Fix login bug",
    column_values: "{\"status\": {\"label\": \"Working on it\"}, \"date4\": {\"date\": \"2026-03-25\"}}"
  ) {
    id name
  }
}
```

**Get item by ID:**

```graphql
{
  items(ids: [ITEM_ID]) {
    id name
    board { id name }
    group { id title }
    column_values { id title text type value }
    updates(limit: 5) { id body created_at creator { name } }
  }
}
```

**Move item to a different group:**

```graphql
mutation {
  move_item_to_group(item_id: ITEM_ID, group_id: "NEW_GROUP_ID") {
    id
  }
}
```

**Delete item:**

```graphql
mutation {
  delete_item(item_id: ITEM_ID) { id }
}
```

**Archive item:**

```graphql
mutation {
  archive_item(item_id: ITEM_ID) { id }
}
```

## Column Values

**Change a single column:**

```graphql
mutation {
  change_column_value(
    item_id: ITEM_ID,
    board_id: BOARD_ID,
    column_id: "status",
    value: "{\"label\": \"Done\"}"
  ) { id }
}
```

**Change multiple columns at once:**

```graphql
mutation {
  change_multiple_column_values(
    item_id: ITEM_ID,
    board_id: BOARD_ID,
    column_values: "{\"status\": {\"label\": \"Done\"}, \"text0\": \"Completed\"}"
  ) { id }
}
```

## Subitems

**Create a subitem:**

```graphql
mutation {
  create_subitem(
    parent_item_id: PARENT_ITEM_ID,
    item_name: "Subtask 1"
  ) { id name board { id } }
}
```

**Get subitems of an item:**

```graphql
{
  items(ids: [PARENT_ITEM_ID]) {
    subitems {
      id name
      column_values { id title text }
    }
  }
}
```

## Updates (Comments)

**Create an update:**

```graphql
mutation {
  create_update(item_id: ITEM_ID, body: "Deployed to staging.") {
    id body created_at
  }
}
```

**List updates on an item:**

```graphql
{
  items(ids: [ITEM_ID]) {
    updates(limit: 10) {
      id body created_at
      creator { id name email }
    }
  }
}
```

**Reply to an update:**

```graphql
mutation {
  create_update(item_id: ITEM_ID, parent_id: UPDATE_ID, body: "Confirmed.") {
    id
  }
}
```

## Columns

**Create a column:**

```graphql
mutation {
  create_column(
    board_id: BOARD_ID,
    title: "Priority",
    column_type: status
  ) { id title }
}
```

**Delete a column:**

```graphql
mutation {
  delete_column(board_id: BOARD_ID, column_id: "COLUMN_ID") { id }
}
```

## Users

**List workspace users:**

```graphql
{
  users(limit: 50) {
    id name email account { id name }
  }
}
```

## Pagination

First page:

```graphql
{
  boards(ids: [BOARD_ID]) {
    items_page(limit: 100) {
      cursor
      items { id name column_values { id text } }
    }
  }
}
```

Subsequent pages (use the `cursor` from the previous response):

```graphql
{
  next_items_page(limit: 100, cursor: "CURSOR_VALUE") {
    cursor
    items { id name column_values { id text } }
  }
}
```

When `cursor` is `null`, there are no more pages.

## Batch Operations

Use GraphQL aliases to run multiple mutations in one request:

```graphql
mutation {
  a: change_column_value(item_id: 111, board_id: BOARD_ID, column_id: "status", value: "{\"label\": \"Done\"}") { id }
  b: change_column_value(item_id: 222, board_id: BOARD_ID, column_id: "status", value: "{\"label\": \"Done\"}") { id }
  c: change_column_value(item_id: 333, board_id: BOARD_ID, column_id: "status", value: "{\"label\": \"Done\"}") { id }
}
```

## curl Template

```bash
curl -s -X POST "https://api.monday.com/graphql" \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "API-Version: 2024-10" \
  -d '{"query": "YOUR_QUERY_HERE"}' | jq
```

For mutations with variables:

```bash
curl -s -X POST "https://api.monday.com/graphql" \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "API-Version: 2024-10" \
  -d '{
    "query": "mutation ($name: String!) { create_item(board_id: BOARD_ID, item_name: $name) { id } }",
    "variables": {"name": "New Item"}
  }' | jq
```

