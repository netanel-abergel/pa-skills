# Changelog

All notable changes to the pa-skills library will be documented in this file.

## [2026-04-18]

### Added
- Graduation gate in `memory-tiering` — dream promotions require score >= 0.70, 2+ recalls, and rationale before landing in MEMORY.md
- Skill manifest (`skills/_manifest.json`) — lightweight index of all 34 skills for fast routing
- Skill failure tracking in `self-learning` — auto-flags skills after 3+ failures in 14 days

### Changed
- `skill-master` now routes via `_manifest.json` before falling back to full REFERENCE.md
- Updated skill descriptions on the website to reflect new features

## [Unreleased]

### Added
- `CONTRIBUTING.md` — standalone contributing guide with skill template, design rules, and PR checklist
- `LICENSE` — MIT license file
- "PRs Welcome" badge in README
- Contribute tab on the website with skill template, design rules, and PR checklist
- 9 missing skills added to the website: chat-history-local, cron-reminders, openclaw-email-orientation, pa-audit-db, personal-crm, quick-reminders, stakeholder-update, whatsapp-diagnostics, whatsapp-voice
- 9 missing skills added to `skills/README.md` with proper categorization

### Fixed
- Removed phantom `skill-scout` skill (listed in indexes but directory never existed)
- Corrected skill count from 41 to 40 across README badge, skill tables, and website
- Updated `skills/README.md` from 32 to 40 skills with reorganized categories

### Changed
- README contributing section now references `CONTRIBUTING.md` instead of inline instructions
- Reorganized `skills/README.md` categories for clarity (merged fragmented sections)

### Previously added
- Open Graph and Twitter meta tags for better link previews
- Favicon using Heleni hero image
- Skill counter in the Skills tab search controls
- Copy button on the Install tab
- Keyboard navigation support for skill cards (tabindex + Enter/Space)
- Canonical URL for SEO
- Compatibility section in README
- Shields.io badges in README
- OpenClaw explainer in README
- GitHub issue templates (New Skill Request, Bug Report) and PR template
- `robots.txt` and `sitemap.xml` for SEO
- Missing `usage-costs` skill added to website Skills tab
- Clickable learning cards that link to relevant skills
- Updated README skill table to include all 32 skills
- Guide tab: added Calendar section with weekly view and booking examples
- Guide tab: added Competitive Analysis section
- Guide tab: added missing items — cancel meeting, filtered board views, project board creation, usage costs query

### Fixed
- Removed hardcoded skill count from meta description
- Consistent install paths across README and website (`~/.openclaw/workspace/skills/`)
- Fixed `maintenance` skill frontmatter name mismatch (`workspace-maintenance` → `maintenance`)
- Updated README skill count guideline to reflect actual library size (32 skills)

## [2.0.0] - 2026-04-04

### Added
- New hero layout with Heleni illustration
- Guide tab with real usage examples
- Must-Have Skills section on Heleni tab
- 13 new skills: dynamic-temperature, git-backup, heleni-whatsapp, meeting-notetaker, meeting-scheduler, memory-architecture, pa-eval, pa-ownership, pa-status, proactive-pa, research-synthesizer, spawn-subagent, storage-router, usage-costs
- Connected Services showcase
- Quick stats (32 skills, 24/7 uptime, 15+ Peer PAs)
- `.context` files learning card

### Changed
- Renamed `whatsapp` skill to `heleni-whatsapp`
- Removed `hebrew-nikud` skill
- Updated skill-master with expanded routing
- Enhanced install.sh with interactive mode

## [1.0.0] - 2025-04-01

### Added
- Initial release with 19 skills
- GitHub Pages website with skill browser, learnings, and FAQ
- Batch installer script (`install.sh`)
- `heleni-best-practices` auto-sync skill

## 2026-04-18 (Evening)
- **self-monitor**: Added root-cause iron law (investigate before fix) and destructive command guard (inspired by gstack /investigate + /guard)
- **self-learning**: Added weekly retro with trend tracking and cron setup (inspired by gstack /retro)
- **skill-master**: Added proactive skill suggestion — detect patterns and suggest skills before being asked
- **Website**: 4 new learnings (root-cause, guard mode, weekly retro, proactive suggestion)
