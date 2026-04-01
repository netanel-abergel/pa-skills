---
name: git-backup
description: "Backup the agent workspace to a GitHub repository. Use when: asked to save/remember something important, after significant changes to memory files, on a schedule, or when asked to push workspace to git. Handles token discovery, repo initialization, and push. If no GitHub token is available, asks the owner for a PAT before proceeding."
---

# Git Backup Skill

Backup your OpenClaw workspace to GitHub automatically.

---

## Token Discovery

Before any git operation, find the token using this priority order:

```bash
find_github_token() {
  # 1. Check git remote (most common)
  TOKEN=$(git -C ~/.openclaw/workspace remote get-url origin 2>/dev/null \
    | grep -oP 'ghp_[A-Za-z0-9]+' | head -1)
  [ -n "$TOKEN" ] && echo "$TOKEN" && return

  # 2. Check environment
  [ -n "$GITHUB_TOKEN" ] && echo "$GITHUB_TOKEN" && return
  [ -n "$GH_TOKEN" ] && echo "$GH_TOKEN" && return

  # 3. Check credentials files
  for f in ~/.credentials/github*.txt ~/.credentials/gh*.txt; do
    [ -f "$f" ] && TOKEN=$(cat "$f") && echo "$TOKEN" && return
  done

  # 4. Check .bashrc
  TOKEN=$(grep -oP 'ghp_[A-Za-z0-9]+' ~/.bashrc 2>/dev/null | head -1)
  [ -n "$TOKEN" ] && echo "$TOKEN" && return

  # Not found
  echo ""
}

TOKEN=$(find_github_token)
```

**If token is empty → ask the owner:**
```
"I need a GitHub Personal Access Token to back up your workspace.
Please go to github.com → Settings → Developer Settings → Personal access tokens → Generate new token
Permissions needed: repo (full)
Then send me the token (starts with ghp_)"
```

Save token when received:
```bash
echo "$PAT" > ~/.credentials/github-token.txt
# Also embed in remote URL for future use:
git -C ~/.openclaw/workspace remote set-url origin \
  "https://${PAT}@github.com/OWNER/REPO.git"
```

---

## Setup (First Time)

### Check if repo exists

```bash
TOKEN=$(find_github_token)
REPO_NAME="my-pa-memory"  # or agent-specific name
OWNER="github-username"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO_NAME")

if [ "$STATUS" = "200" ]; then
  echo "Repo exists"
elif [ "$STATUS" = "404" ]; then
  echo "Need to create repo"
fi
```

### Create repo if needed

```bash
curl -s -X POST "https://api.github.com/user/repos" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"$REPO_NAME\", \"private\": true, \"description\": \"PA workspace backup\"}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('html_url','error: '+str(d)))"
```

### Initialize git in workspace

```bash
cd ~/.openclaw/workspace
git init
git config user.email "agent@openclaw.ai"
git config user.name "PA Agent"
git remote add origin "https://$TOKEN@github.com/$OWNER/$REPO_NAME.git"

# Create .gitignore
cat > .gitignore << 'EOF'
*.log
.env
credentials/
*.key
*.pem
node_modules/
__pycache__/
.DS_Store
EOF

git add -A
git commit -m "Initial workspace backup"
git push -u origin main
```

---

## Backup (Regular Use)

### Quick backup

```bash
backup_workspace() {
  WORKSPACE="${1:-$HOME/.openclaw/workspace}"
  cd "$WORKSPACE" || return 1

  # Check token
  TOKEN=$(find_github_token)
  if [ -z "$TOKEN" ]; then
    echo "BLOCKED: No GitHub token found. Ask owner for PAT."
    return 1
  fi

  # Check git is initialized
  if [ ! -d ".git" ]; then
    echo "BLOCKED: Git not initialized. Run setup first."
    return 1
  fi

  # Commit and push
  git add -A
  CHANGES=$(git diff --cached --name-only | wc -l)
  
  if [ "$CHANGES" -eq 0 ]; then
    echo "Nothing to backup — workspace unchanged."
    return 0
  fi

  DATE=$(date -u +%Y-%m-%d\ %H:%M\ UTC)
  git commit -m "Auto backup $DATE"
  git push origin main 2>&1

  echo "✅ Backup complete — $CHANGES files updated."
}

backup_workspace
```

---

## Trigger Conditions

Run a backup when:
- Owner says "remember this" / "save this" / "שמרי"
- Daily at a scheduled time (cron)
- After updating MEMORY.md, SOUL.md, or daily notes
- After a significant task is completed
- Before context compaction

### Cron config

```json
{
  "jobs": [
    {
      "id": "workspace-backup",
      "schedule": "0 */6 * * *",
      "timezone": "UTC",
      "task": "Run git backup of the workspace to GitHub. Use the git-backup skill. Commit all changes and push. Report DONE or BLOCKED.",
      "delivery": {
        "mode": "silent"
      }
    }
  ]
}
```

Runs every 6 hours silently. Change to `"0 23 * * *"` for nightly only.

---

## What to Back Up

Always include:
- `MEMORY.md` — long-term memory
- `SOUL.md` — behavior config
- `AGENTS.md` — workspace rules
- `TOOLS.md` — environment notes
- `memory/` — daily notes
- `skills/` — installed skills
- `.learnings/` — corrections and learnings
- `data/` — PA directory and other data
- `config/` — MCP and other configs

Always exclude (add to .gitignore):
- API keys / tokens / secrets
- `credentials/` directory
- Log files
- Node modules

---

## Troubleshooting

**Push rejected (non-fast-forward):**
```bash
git pull --rebase origin main && git push origin main
```

**Token expired / 401:**
```bash
# Ask owner for new PAT, then update remote:
git remote set-url origin "https://NEW_TOKEN@github.com/OWNER/REPO.git"
```

**Repo doesn't exist (404):**
Run setup section above to create it.

**Large files rejected:**
```bash
# Find and exclude large files
find . -size +5M -not -path './.git/*' >> .gitignore
git rm -r --cached .
git add -A
git commit -m "Remove large files"
```

---

## Model Notes

- Any model can run this skill — pure shell operations
- No reasoning required; just follow the steps in order
- If blocked on token: escalate to owner immediately, do not retry without token
