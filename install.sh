#!/bin/bash
# Heleni AI PA — Full Package Installer
# Usage: curl -fsSL https://netanel-abergel.github.io/pa-skills/install.sh | bash

set -e

REPO="https://github.com/netanel-abergel/pa-skills.git"
SKILLS_DIR="${OPENCLAW_WORKSPACE:-/opt/ocana/openclaw/workspace}/skills"
TMPDIR_CLONE=$(mktemp -d)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}⚡ Heleni AI PA — Full Package${NC}"
echo -e "${BLUE}   Installing all skills into: ${SKILLS_DIR}${NC}"
echo ""

# Clone repo
echo -e "  → Cloning pa-skills..."
git clone --depth=1 --quiet "$REPO" "$TMPDIR_CLONE"

# Skills to install
SKILLS=(
  unanswered-messages
  proactive-pa
  monday-for-agents
  ai-pa
  pa-onboarding
  owner-briefing
  self-monitor
  whatsapp-diagnostics
  pa-status
  meeting-scheduler
  skill-master
  git-backup
  billing-monitor
  spawn-subagent
)

mkdir -p "$SKILLS_DIR"

SUCCESS=0
SKIP=0

for skill in "${SKILLS[@]}"; do
  src="$TMPDIR_CLONE/skills/$skill"
  dst="$SKILLS_DIR/$skill"

  if [ ! -d "$src" ]; then
    echo -e "  ${YELLOW}⚠ $skill — not found in repo, skipping${NC}"
    ((SKIP++))
    continue
  fi

  if [ -d "$dst" ]; then
    echo -e "  ${YELLOW}↺ $skill — already installed, updating${NC}"
    rm -rf "$dst"
  else
    echo -e "  ${GREEN}✓ $skill${NC}"
  fi

  cp -r "$src" "$dst"
  ((SUCCESS++))
done

# Cleanup
rm -rf "$TMPDIR_CLONE"

echo ""
echo -e "${BOLD}Done!${NC} Installed ${GREEN}${SUCCESS}${NC} skills."
if [ "$SKIP" -gt 0 ]; then
  echo -e "Skipped: ${YELLOW}${SKIP}${NC}"
fi
echo ""
echo -e "  ${BLUE}Restart your OpenClaw gateway to activate:${NC}"
echo -e "  ${BOLD}openclaw gateway restart${NC}"
echo ""
