# Self-Reflection Skill

When the owner wants to improve how you operate, follow this process. The goal: turn vague dissatisfaction into specific, technical changes to your own system.

## Process

### 1. Understand the Problem (2-3 questions max)
Ask focused questions to pin down:
- What specifically is wrong? (Get a concrete example)
- What would "good" look like? (Expected vs actual behavior)
- How important is this? (Tweak vs fundamental change)

Don't over-ask. If the complaint is clear enough, skip to step 2.

### 2. Deep System Scan
Audit ALL relevant parts of your system. Read before changing:

#### Core Identity & Behavior
- Persona, boundaries, tone rules
- Operating instructions
- User profile, preferences
- Long-term memory and facts
- Tool-specific notes

#### Skills (behavior patterns)
- All custom skills
- Bundled skills
- Workspace skills override bundled on name collision

#### Configuration
- Model, tools, channels, heartbeat, queue mode, streaming, etc.

#### Cron Jobs
- All scheduled jobs (timing/frequency related issues)

Read broadly, change surgically. Scan everything related, modify only what's needed.

### 3. Diagnose & Propose
Present findings:
1. Root cause - what causes the unwanted behavior
2. Proposed changes - specific files and edits
3. Side effects - anything else affected
4. Alternatives - multiple approaches if they exist

### 4. Implement Changes
After approval, make all changes:
- Edit workspace files (persona, memory, etc.)
- Edit/create/modify skills
- Update config
- Add/modify/remove cron jobs

Every change must be technically concrete. "I'll be more careful" is NOT a valid change.

### 5. Verify & Document
- Test the change if possible
- Document what changed and why
- Commit workspace changes

## Important Principles
- Scan everything, change only what's needed
- No fake fixes - if you can't find a technical change, say so
- Owner approves changes - present the plan, get approval, then execute
- Compound improvements - each reflection makes the system permanently better
- Be honest about limitations - some behaviors are model-level
