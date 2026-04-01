---
name: openclaw-email-orientation
description: Explain how email and Google Calendar work for OpenClaw agents, including the distinction between agent email and owner email, how gog and the Google Workspace skill are used, where related credentials/config live, and how to troubleshoot common setup or access issues. Use when someone asks how an OpenClaw agent accesses Gmail/Google Workspace/Calendar, where credentials are stored, how to use the agent inbox, how to give the agent write access to the owner's calendar, or how to guide another agent/user through the email or calendar setup model.
---

# OpenClaw Email & Calendar Orientation

Use this skill to explain and troubleshoot how email and Google Calendar work for OpenClaw agents.

## Core model
- Explain that **owner** and **agent** are different concepts in OpenClaw.
- Explain that each **agent** is created with its own **Google Workspace / G Suite account**.
- Explain that the agent can act through its own mailbox and related Google Workspace tools.
- Explain that agents commonly use **gog** plus the **Google Workspace skill** to work with Gmail, Calendar, Drive, Contacts, Sheets, and Docs.

## What to explain first
When someone is confused, start with this concise model:
1. The **owner** is the human who owns or manages the agent.
2. The **agent** is the AI worker running in OpenClaw.
3. The **agent email** belongs to the agent account, not automatically to the owner.
4. Google Workspace access is typically done through `gog` after auth is configured.

## Local paths and files
Share only the paths that are needed for setup/troubleshooting.

- gog OAuth client credentials: `~/.openclaw/.gog/credentials.json`
- OpenClaw auth profiles: `~/.openclaw/agents/main/agent/auth-profiles.json`
- Workspace skill reference: `~/.openclaw/workspace/skills/gog/SKILL.md`

Important:
- Do **not** reveal secret contents from these files in chat.
- It is okay to mention the file paths when helping with setup or troubleshooting.
- `auth-profiles.json` and `.gog/credentials.json` are protected files; do not modify them casually.

## How to use gog
Read `~/.openclaw/workspace/skills/gog/SKILL.md` if you need exact command examples.

Typical guidance:
- Authenticate credentials: `gog auth credentials /path/to/client_secret.json`
- Add an account: `gog auth add you@company.com --services gmail,calendar,drive,contacts,sheets,docs`
- List accounts: `gog auth list`
- Use an account with `GOG_ACCOUNT=you@company.com`

Useful examples:
- Search Gmail: `gog gmail search 'newer_than:7d' --max 10`
- Send mail: `gog gmail send --to a@b.com --subject "Hi" --body "Hello"`
- List calendar events: `gog calendar events <calendarId> --from <iso> --to <iso>`
- Create calendar event: `gog calendar create <calendarId> --summary "Meeting" --start <iso> --end <iso>`

## Google Calendar — Owner Calendar Access
Agents often need to read and write the **owner's** Google Calendar (not just their own).

Key distinction:
- The **agent email** (e.g. `midgee@openclaw.ai`) is set up by default.
- The **owner calendar** (e.g. `doron@monday.com`) requires explicit sharing + auth.

To give the agent write access to the owner's calendar:
1. Owner goes to Google Calendar → Settings → Share with specific people
2. Adds the agent email with **"Make changes to events"** permission
3. Agent runs: `gog auth add owner@company.com --services calendar` (or re-auths with calendar scope)
4. Agent uses `GOG_ACCOUNT=owner@company.com` when calling calendar commands

Common issue — calendar shows "connected" in OpenClaw dashboard but agent can't write:
- The connection in the dashboard may reflect OAuth at the agent-email level only
- If the owner's calendar is a separate Google account, it needs to be separately shared and authed
- Re-auth with `--services calendar` and verify write scope was granted (not just read)
- Test with: `gog calendar create primary --summary "Test" --start <now+1h> --end <now+2h>`
- If error mentions "insufficient permissions" → scope issue, redo OAuth with write permissions

## Troubleshooting
When helping someone debug, walk through these checks:
1. Confirm whether they mean the **owner email** or the **agent email**.
2. Confirm `gog` is installed and available in PATH.
3. Confirm the account was added to `gog`.
4. Confirm the needed Google services were authorized — especially **write** scope for calendar.
5. If keyring/password issues appear, explain that local secret storage/keyring configuration may be required.
6. If access fails, verify they are using the correct account context (`GOG_ACCOUNT`).
7. For calendar write failures: check if the owner shared their calendar with the agent email, and whether write permission was explicitly granted.

## Response style
- Be explicit about the owner-vs-agent distinction.
- Mirror the language used by the person asking.
- Prefer a short practical explanation first, then commands/examples.
- If they ask for exact usage, provide step-by-step guidance.
- If they ask where things are stored, provide the path but never dump secrets.

## Model Compatibility

This skill is an **orientation guide** — it explains concepts and gives commands. Any LLM model can use it.

| Task | Minimum Model |
|---|---|
| Explaining the owner-vs-agent distinction | Any |
| Providing gog command examples | Any |
| Troubleshooting calendar auth issues | Small–Medium |
| Diagnosing multi-account or domain-restriction issues | Medium recommended |

No model-specific APIs or reasoning features are required. All commands use the `gog` CLI, which is model-agnostic.
