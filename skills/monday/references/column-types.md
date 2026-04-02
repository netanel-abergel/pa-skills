# Monday.com Column Value Formats

The `value` parameter in `change_column_value` and `change_multiple_column_values` requires a JSON-encoded string. Each column type has its own format.

## Status

```json
{"label": "Done"}
```

Or by index:

```json
{"index": 1}
```

## Text

Plain string (no wrapper object):

```json
"Hello world"
```

## Numbers

```json
"42"
```

## Date

```json
{"date": "2026-03-25"}
```

With time:

```json
{"date": "2026-03-25", "time": "14:30:00"}
```

## Person / People

```json
{"personsAndTeams": [{"id": 12345, "kind": "person"}]}
```

Multiple:

```json
{"personsAndTeams": [{"id": 12345, "kind": "person"}, {"id": 67890, "kind": "person"}]}
```

## Dropdown

By label:

```json
{"labels": ["Option A", "Option B"]}
```

By ID:

```json
{"ids": [1, 3]}
```

## Checkbox

```json
{"checked": true}
```

## Email

```json
{"email": "name@example.com", "text": "name@example.com"}
```

## Link / URL

```json
{"url": "https://example.com", "text": "Example"}
```

## Phone

```json
{"phone": "+1234567890", "countryShortName": "US"}
```

## Long Text

```json
{"text": "This is a longer description with details."}
```

## Timeline (date range)

```json
{"from": "2026-03-01", "to": "2026-03-31"}
```

## Hour

```json
{"hour": 14, "minute": 30}
```

## Rating

```json
{"rating": 4}
```

## Week

```json
{"week": {"startDate": "2026-03-23", "endDate": "2026-03-29"}}
```

## World Clock (timezone)

```json
{"timezone": "America/New_York"}
```

## Tags

```json
{"tag_ids": [123, 456]}
```

## Country

```json
{"countryCode": "US", "countryName": "United States"}
```

## Color Picker

```json
{"color": {"hex": "#FF5733"}}
```

## Dependency / Connect Boards (relation)

```json
{"item_ids": [12345, 67890]}
```

## File (upload via API)

Files cannot be set via `change_column_value`. Use the `add_file_to_column` mutation:

```graphql
mutation ($file: File!) {
  add_file_to_column(
    item_id: ITEM_ID,
    column_id: "files",
    file: $file
  ) { id }
}
```

## Clearing a column value

Set the value to an empty JSON object or `null`:

```json
{}
```

## Example: setting multiple columns at once

```bash
curl -s -X POST "https://api.monday.com/graphql" \
  -H "Authorization: $MONDAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { change_multiple_column_values(item_id: ITEM_ID, board_id: BOARD_ID, column_values: \"{\\\"status\\\": {\\\"label\\\": \\\"Working on it\\\"}, \\\"date4\\\": {\\\"date\\\": \\\"2026-03-25\\\"}, \\\"person\\\": {\\\"personsAndTeams\\\": [{\\\"id\\\": 12345, \\\"kind\\\": \\\"person\\\"}]}}\") { id } }"
  }' | jq
```

Note the triple-escaping: the `column_values` parameter is a JSON string inside a GraphQL string inside a JSON request body.

