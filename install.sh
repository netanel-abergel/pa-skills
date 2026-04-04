#!/bin/bash
# Heleni AI PA — Full Bootstrap Installer
# Usage: curl -fsSL https://netanel-abergel.github.io/pa-skills/install.sh | bash
#
# What this does:
# 1. Installs all 31 skills from pa-skills into your OpenClaw workspace
# 2. Sets up required directory structure (memory/, data/, inbox/, skills/)
# 3. Creates starter files (PA_LIST.md, heartbeat-state.json, pending.json)
# 4. Prints next steps for SOUL.md and .context setup
#
# Time to complete: ~2 minutes

set -e

REPO="https://github.com/netanel-abergel/pa-skills.git"
WORKSPACE="${OPENCLAW_WORKSPACE:-/opt/ocana/openclaw/workspace}"
SKILLS_DIR="$WORKSPACE/skills"
TMPDIR_CLONE=$(mktemp -d)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}⚡ Heleni AI PA — Full Bootstrap${NC}"
echo -e "${BLUE}   Workspace: ${WORKSPACE}${NC}"
echo ""

# ── 1. Clone repo ──────────────────────────────────────────────────────────────
echo -e "  → Cloning pa-skills..."
git clone --depth=1 --quiet "$REPO" "$TMPDIR_CLONE"

# ── 2. Install all skills ──────────────────────────────────────────────────────
echo -e "  → Installing skills..."
mkdir -p "$SKILLS_DIR"

SUCCESS=0
SKIP=0

for skill_dir in "$TMPDIR_CLONE/skills"/*/; do
  skill=$(basename "$skill_dir")
  dst="$SKILLS_DIR/$skill"

  if [ -d "$dst" ]; then
    echo -e "    ${YELLOW}↺ $skill — updating${NC}"
    rm -rf "$dst"
  else
    echo -e "    ${GREEN}✓ $skill${NC}"
  fi

  cp -r "$skill_dir" "$dst"
  ((SUCCESS++))
done

# ── 3. Directory structure ─────────────────────────────────────────────────────
echo -e "  → Setting up directory structure..."
mkdir -p "$WORKSPACE/memory/whatsapp/groups"
mkdir -p "$WORKSPACE/memory/whatsapp/dms"
mkdir -p "$WORKSPACE/data"
mkdir -p "$WORKSPACE/inbox"
mkdir -p "$WORKSPACE/logs"
mkdir -p "$WORKSPACE/.learnings"
mkdir -p "$WORKSPACE/tasks"

# ── 4. Starter files ───────────────────────────────────────────────────────────
# heartbeat state
if [ ! -f "$WORKSPACE/memory/heartbeat-state.json" ]; then
  cat > "$WORKSPACE/memory/heartbeat-state.json" << 'EOF'
{
  "lastChecks": {
    "unanswered": null,
    "calendar": null,
    "crons": null,
    "email": null
  }
}
EOF
  echo -e "    ${GREEN}✓ memory/heartbeat-state.json${NC}"
fi

# inbox
if [ ! -f "$WORKSPACE/inbox/pending.json" ]; then
  cat > "$WORKSPACE/inbox/pending.json" << 'EOF'
{
  "version": 1,
  "messages": []
}
EOF
  echo -e "    ${GREEN}✓ inbox/pending.json${NC}"
fi

# PA_LIST.md starter
if [ ! -f "$WORKSPACE/PA_LIST.md" ]; then
  cat > "$WORKSPACE/PA_LIST.md" << 'EOF'
# PA & Contacts Index

## Active PAs

| PA Name | PA Phone | Owner | Owner Phone | Owner Role | Status | Notes |
|---|---|---|---|---|---|---|
| YourPA | +1XXXXXXXXXX | Owner Name | +1XXXXXXXXXX | Role | ✅ Active | |

## PA Sync List (for pa-network-daily-sync)

### DM Targets
# Add PA phone numbers here — one per line

### Group Targets
# Add group JIDs here
EOF
  echo -e "    ${GREEN}✓ PA_LIST.md (starter)${NC}"
fi

# .gitignore
if [ ! -f "$WORKSPACE/.gitignore" ]; then
  cat > "$WORKSPACE/.gitignore" << 'EOF'
*.log
.env
credentials/
*.key
*.pem
node_modules/
__pycache__/
.DS_Store
skills/**/.context
EOF
  echo -e "    ${GREEN}✓ .gitignore${NC}"
fi

# ── 5. Cleanup ─────────────────────────────────────────────────────────────────
rm -rf "$TMPDIR_CLONE"

# ── 6. Summary ─────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}✅ Done!${NC} Installed ${GREEN}${SUCCESS}${NC} skills."
echo ""
echo -e "${BOLD}Next steps:${NC}"
echo ""
echo -e "  ${BLUE}1. Create your SOUL.md${NC} — define who your PA is and how she behaves"
echo -e "     Copy from: ${BOLD}https://netanel-abergel.github.io/pa-skills/${NC}"
echo ""
echo -e "  ${BLUE}2. Create .context files${NC} — add your personal IDs to each skill:"
echo -e "     Each skill has a 'Load Local Context' section in its SKILL.md"
echo -e "     Example: ${BOLD}skills/storage-router/.context${NC}"
echo -e "     ${YELLOW}Note: .context files are gitignored — they stay private${NC}"
echo ""
echo -e "  ${BLUE}3. Update PA_LIST.md${NC} — add your PA network contacts"
echo ""
echo -e "  ${BLUE}4. Restart OpenClaw gateway:${NC}"
echo -e "     ${BOLD}openclaw gateway restart${NC}"
echo ""
echo -e "  ${BLUE}5. Test:${NC} Send yourself 'מה הסטטוס' and verify supervisor skill responds"
echo ""
echo -e "${BOLD}Docs:${NC} https://netanel-abergel.github.io/pa-skills/"
echo ""
