#!/usr/bin/env bash
# sync-pa-skills.sh — Sync local skills to netanel-abergel/pa-skills GitHub repo
# Usage: bash sync-pa-skills.sh
# Filters: skips .context files, data/ directories, README.md at root

TOKEN=$(git -C /opt/ocana/openclaw/workspace remote get-url origin 2>/dev/null | sed 's/.*x-access-token:\([^@]*\)@.*/\1/')
REPO="netanel-abergel/pa-skills"
LOCAL_SKILLS="/opt/ocana/openclaw/workspace/skills"

# Files/patterns to NEVER sync to public repo
SKIP_PATTERNS=(
  ".context"
  "data/"
  "context.md"
  ".env"
  "credentials"
  "secrets"
)

should_skip() {
  local filepath="$1"
  for pattern in "${SKIP_PATTERNS[@]}"; do
    if echo "$filepath" | grep -q "$pattern"; then
      return 0  # skip
    fi
  done
  return 1  # don't skip
}

upload_file() {
  local local_path="$1"
  local repo_path="$2"
  
  if should_skip "$repo_path"; then
    echo "  SKIP (private): $repo_path"
    return
  fi

  local content
  content=$(base64 -w 0 < "$local_path")
  local sha
  sha=$(curl -s -H "Authorization: token $TOKEN" \
    "https://api.github.com/repos/$REPO/contents/$repo_path" | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('sha',''))" 2>/dev/null)

  local payload
  if [ -n "$sha" ]; then
    payload="{\"message\": \"sync: update from heleni workspace\", \"content\": \"$content\", \"sha\": \"$sha\"}"
  else
    payload="{\"message\": \"sync: add from heleni workspace\", \"content\": \"$content\"}"
  fi

  local result
  result=$(curl -s -X PUT \
    -H "Authorization: token $TOKEN" \
    -H "Content-Type: application/json" \
    "https://api.github.com/repos/$REPO/contents/$repo_path" \
    -d "$payload" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if 'content' in d else 'FAIL: '+str(d)[:80])")
  echo "  $repo_path → $result"
}

SUCCESS=0
FAIL=0

for skill_dir in "$LOCAL_SKILLS"/*/; do
  skill=$(basename "$skill_dir")
  [ "$skill" = "README.md" ] && continue
  [ -f "$skill_dir" ] && continue  # skip files at root level

  echo "[$skill]"
  find "$skill_dir" -type f | while read -r file; do
    rel="${file#$LOCAL_SKILLS/}"
    upload_file "$file" "skills/$rel"
  done
done

echo ""
echo "Done."
