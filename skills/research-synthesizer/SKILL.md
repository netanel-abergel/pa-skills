---
name: research-synthesizer
version: "1.1.0"
description: "Multi-source research synthesizer. Runs 3-5 parallel web searches, deduplicates, and returns a cited answer under ~400 words. Hebrew + English supported."
triggers:
  - "research"
  - "find out about"
  - "synthesize"
  - "look up"
---

# Research Synthesizer Skill

Multi-source search → deduplicate → synthesize → cite.

## When to Use
- "research [topic]"
- "find out about [topic]"
- "look up [topic]"

## Process

### Step 0: Clarify the Brief
For companies/products: verify OUR product positioning first.

### Step 0b: Question Decomposition
For broad questions, decompose into sub-questions first:
Input: "Compare X to Y"
→ Sub-Qs: What is X? What is Y? Who built each? Core features? Pricing?

### Step 1: Classify
- Hebrew? → search both Hebrew AND English
- Factual / trend / technical / recent event?

### Step 2: Generate 3-5 Query Variants
Q1: Direct question
Q2: Keywords only
Q3: "how does X work" / "X explained"
Q4: Hebrew (if applicable)
Q5: "[topic] 2025 latest"

### Step 2b: Verify Companies
MANDATORY: web_fetch their homepage before writing anything.
Never assume capabilities from category name.

### Step 3: Run Searches (parallel)
Collect: title, URL, snippet.

### Step 4: Deduplicate & Score
- Remove duplicates + off-topic results
- Score: High (official docs, major press) / Medium (reputable blogs) / Low (forums)
- For fast-moving topics: filter out >2yr old results

### Step 5: Synthesize
Format:
🔍 [Topic]
[3-5 sentence direct answer]
📌 Key Points:
• ...
📚 Sources:
1. [Title] — [URL]

Max ~400 words. Match user's language.

## Rules
1. Always cite ≥2 sources (≥5 for competitive analysis)
2. Verify companies from their own site
3. Hebrew in → Hebrew out
4. Flag conflicts or stale data
5. No raw dumps — synthesize
6. After delivering: save summary to memory if topic was important

## Credit
v1.1 improvements contributed by Laika (Omri's PA), April 2026.
