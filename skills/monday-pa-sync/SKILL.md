# monday-pa-sync

Sync open monday.com board items to today's PA memory file automatically.

## When to use
- Owner asks: "what's on my monday board?"
- Daily morning routine
- Cron: sync tasks at start of day

## Steps
1. Load API token from `~/.credentials/monday-token.txt`
2. Query board via monday.com GraphQL API
3. Filter open/in-progress items
4. Append structured task list to `memory/YYYY-MM-DD.md`
5. Deduplicate — safe to run multiple times

## Config (.context file)
Store in `skills/monday-pa-sync/.context`:
```
MONDAY_BOARD_ID=your_board_id
MONDAY_WORKSPACE=your_workspace_name
MEMORY_DIR=/opt/ocana/openclaw/workspace/memory
```

## Cron example
```
0 8 * * * /path/to/skills/monday-pa-sync/scripts/sync.sh
```

## Output (appended to memory file)
```
## Monday Tasks (synced 08:01)
- [ ] Task name — [in progress] — due: 2026-04-08
```

## Dependencies
- `curl`, `jq`
- monday.com API token (boards:read scope)

## Notes
- Uses .context for portability — no hard-coded IDs
- Skips done/archived items
- Hebrew item names supported

## Credit
Contributed by Selena (Daniel's PA), April 2026.
