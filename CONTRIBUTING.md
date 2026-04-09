# Contributing to Heleni PA Skills

Thanks for your interest in contributing! This library grows through real-world experience — every skill here was born from production use.

## Ways to Contribute

### 1. Add a New Skill

The most impactful contribution. If your AI PA needs something that doesn't exist here, build it and share it.

### 2. Add Production Caveats

Already using a skill? Add what broke, what surprised you, and what workaround you found. A `## Caveats` section with real failure modes is more valuable than a new feature.

### 3. Report Issues

Found a bug in a skill or the website? [Open an issue](https://github.com/netanel-abergel/pa-skills/issues/new/choose) using the provided templates.

### 4. Improve Documentation

Fix typos, clarify steps, add examples. Small improvements compound.

---

## Creating a New Skill

### 1. Set Up the Directory

```bash
mkdir skills/<skill-name>
```

### 2. Create SKILL.md

Every skill needs a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: skill-name
description: "What it does. Use when: the PA needs to..."
---

# Skill Name

## Step 1 — ...

## Step 2 — ...

## Caveats

_None documented yet — add yours after running in production._
```

### 3. Follow the Design Rules

- **One domain = one skill.** Users think in domains, not tools.
- **Keep SKILL.md generic.** No hardcoded IDs, phone numbers, JIDs, or internal names.
- **Agent-specific data goes in `.context` files** (gitignored from this repo).
- **Each skill needs one clear "Use when:" sentence** in the description.
- **Include a `## Caveats` section** — even if empty with a placeholder. Document real failure modes, version requirements, and gotchas from production.
- **Universal rules go in SOUL.md**, not in skills. Skills are triggered on demand.
- **Diagnostics = appendix.** Never a standalone skill.

### 4. The `.context` Pattern

Skills must be fully portable. Store agent-specific configuration in a `.context` file:

```
skills/
  your-skill/
    SKILL.md      ← generic, synced here
    .context      ← agent-specific values, stays private
```

Example `.context`:

```bash
# your-skill — Local Context (not synced to pa-skills)
OWNER_PHONE=+1XXXXXXXXXX
BOARD_ID=12345678
```

Add `skills/**/.context` to your `.gitignore`.

---

## Submitting a Pull Request

### Before You Submit

1. **Privacy review** — scan for internal names, IDs, phone numbers, credentials
2. **Test with at least one LLM** — Claude, GPT, Gemini, Llama, or Mistral
3. **Update the indexes:**
   - `skills/README.md` — add your skill to the right category
   - Root `README.md` — add your skill to the skill table
   - `CHANGELOG.md` — add an entry under `[Unreleased]`

### PR Checklist

Your PR should pass this checklist (also in the PR template):

- [ ] `SKILL.md` has YAML frontmatter (`name`, `description`)
- [ ] Description includes a clear "Use when:" sentence
- [ ] Skill directory is under `skills/<skill-name>/`
- [ ] `skills/README.md` updated with the new/modified skill
- [ ] Root `README.md` skill table updated
- [ ] `CHANGELOG.md` updated
- [ ] Tested with at least one LLM (which one?)

### What Makes a Great PR

- **Real failure modes** in the Caveats section — "here's what happened when I actually ran it"
- **Clear trigger phrases** — what should the user say to activate this skill?
- **Minimal scope** — one domain, one skill. Don't bundle unrelated changes.

---

## Skill Categories

When adding to the indexes, place your skill in the right category:

| Category | What belongs here |
|----------|-------------------|
| **Core** | Onboarding, routing, evaluation, status dashboards |
| **Communication** | WhatsApp, meetings, scheduling, CRM, stakeholder updates |
| **Integrations** | Calendar, monday.com, email, YouTube, external service setup |
| **Self-Improvement** | Learning, monitoring, analytics, best practices, memory |
| **Operations** | Maintenance, billing, backups, costs, reminders, diagnostics |

---

## Code of Conduct

Be respectful, constructive, and focused on improving the library. We're building tools that help AI agents help people — keep that spirit in every interaction.

---

## Questions?

Open a [discussion](https://github.com/netanel-abergel/pa-skills/issues) or check the [website](https://netanel-abergel.github.io/pa-skills/) for the full learnings library.
