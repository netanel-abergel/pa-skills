# Changelog

All notable changes to the pa-skills library will be documented in this file.

## [Unreleased]

### Added
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

### Fixed
- Removed hardcoded skill count from meta description
- Consistent install paths across README and website (`~/.openclaw/workspace/skills/`)

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
