---
name: research-synthesizer
description: "Multi-source research synthesizer. Takes a question, runs 3-5 parallel web searches with varied phrasings, deduplicates, and returns a cited, concise answer. For Hebrew questions, searches in both Hebrew and English. Output is always under ~400 words."
triggers:
  - "תחקר"
  - "חפש לי"
  - "research"
  - "find out about"
  - "what do you know about"
  - "synthesize"
  - "תסכם לי מחקר"
  - "מה אתה יודע על"
  - "תמצא לי מידע"
  - "look up"
---

# Research Synthesizer Skill

Multi-source search → deduplicate → synthesize → cite. Concise answer under ~400 words, always.

---

## When to Use

Trigger phrases:
- "תחקר [topic]" / "research [topic]"
- "חפש לי [topic]" / "find out about [topic]"
- "what do you know about [topic]"
- "synthesize [topic]"
- "מה אתה יודע על [topic]"
- "תמצא לי מידע על [topic]"
- "look up [topic]"

---

## Step-by-Step Process

### Step 0: Question Decomposition (GPT Researcher Pattern)

Before searching, decompose the question into specific sub-questions:

```
Input: "What is Paperclip and how does it compare to monday.com?"

Sub-questions:
1. What is Paperclip? What does it do?
2. Who built it and when?
3. What are its core features?
4. How is it positioned vs. project management tools?
5. What does monday.com offer that Paperclip doesn't (and vice versa)?
```

**Rule:** For broad or multi-faceted questions (competitive analysis, "explain X", "compare A and B") — always decompose first. For simple factual questions ("who founded X", "when did Y happen") — skip this step.

Each sub-question becomes its own search query. This produces deeper, less biased results than 5 phrasings of the same question.

---

### Step 1: Classify the Question

Before searching:
- **Language:** Is the question in Hebrew? → search in both Hebrew AND English
- **Type:** Factual? Opinion/trend? Technical? Recent event?
- **Scope:** Narrow (specific fact) or broad (overview topic)?

Adjust query phrasings accordingly.

### Step 2: Generate Query Variants

Create 3–5 distinct query phrasings to maximize coverage and reduce bias:

| Variant | Strategy |
|---|---|
| Q1 | Direct question phrasing |
| Q2 | Keyword-only (no question words) |
| Q3 | "best [topic] explained" / "how does X work" |
| Q4 | Hebrew translation (if applicable) |
| Q5 | Recent angle: "[topic] 2024 2025" or "[topic] latest" |

**Example — question: "What is LangGraph?"**
- Q1: "What is LangGraph and how does it work"
- Q2: "LangGraph framework overview"
- Q3: "LangGraph tutorial explained"
- Q4: *(skip — English topic)*
- Q5: "LangGraph 2024 use cases"

**Example — question: "מה זה LangGraph?"**
- Q1: "What is LangGraph and how does it work"
- Q2: "LangGraph framework overview"
- Q3: "LangGraph explained simply"
- Q4: "LangGraph מה זה"
- Q5: "LangGraph 2025 latest"

### Step 3: Run Searches (Parallel)

Run all query variants using `web_search`. Collect:
- Title
- URL
- Snippet

Do not fetch full page content unless snippet is insufficient.

### Step 4: Deduplicate, Filter & Score Sources

From all results:
1. Remove duplicate URLs
2. Remove results that don't address the question
3. Remove results older than 2 years for fast-moving topics (AI, tech, news)
4. Score source credibility:
   - **High:** Official docs, peer-reviewed, major publications (TechCrunch, Wired, HBR)
   - **Medium:** Reputable blogs, GitHub repos, well-known newsletters
   - **Low:** Forums, anonymous posts, marketing pages
5. Prioritize high-credibility sources. If only low-credibility sources available — flag it.

Target: 5–10 sources for deep research, 3–5 for quick questions.

### Step 5: Synthesize

Write the answer in this format:

```
[3–5 sentence summary that directly answers the question]

Key points:
• [point 1]
• [point 2]
• [point 3]
• [point 4 — optional]

Sources:
1. [Title] — [URL]
2. [Title] — [URL]
3. [Title] — [URL]
```

**Synthesis rules:**
- Lead with the direct answer, not background
- Use the user's language (Hebrew question → Hebrew answer)
- Max ~400 words total
- If sources conflict → note the disagreement briefly
- If information is outdated → flag it

### Step 6: Deliver

Send the synthesized answer. Do NOT:
- Dump raw search results
- List every source found
- Add filler like "Great question!" or "I searched the web for..."
- Pad with unnecessary caveats

---

## Output Format Template

```
🔍 [Topic]

[Direct 3-5 sentence answer]

📌 עיקרי הנקודות / Key Points:
• ...
• ...
• ...

📚 מקורות / Sources:
1. [Title] — [URL]
2. [Title] — [URL]
3. [Title] — [URL]
```

---

## Example

**Input:** "תחקר — מה זה Model Context Protocol?"

**Output:**

```
🔍 Model Context Protocol (MCP)

Model Context Protocol (MCP) הוא תקן פתוח שפיתחה Anthropic המאפשר ל-LLMs להתחבר בצורה אחידה לכלים, APIs ומקורות נתונים חיצוניים. במקום שכל אינטגרציה תדרוש קוד מותאם אישית, MCP מגדיר שפה משותפת בין המודל לשרת הכלים. זה מפשט בניית agents ומאפשר שימוש חוזר בכלים בין פלטפורמות שונות.

📌 עיקרי הנקודות:
• פרוטוקול client-server: ה-LLM הוא ה-client, הכלים הם servers
• תמיכה ב-stdio ו-HTTP transport
• מאפשר: tool calling, resource access, prompts
• אימוץ רחב: Claude, Cursor, VS Code, ועוד
• קוד פתוח — SDK זמין ל-Python, TypeScript, Java

📚 מקורות:
1. MCP Official Docs — https://modelcontextprotocol.io
2. Anthropic MCP Announcement — https://www.anthropic.com/news/model-context-protocol
3. MCP GitHub — https://github.com/modelcontextprotocol
```

---

## Hebrew Search Strategy

For Hebrew questions, always search in **both languages**:

| Search | Language | Goal |
|---|---|---|
| Q1–Q2 | English | Get the most content (English web is larger) |
| Q3 | Hebrew | Find Israeli/Hebrew-specific context |
| Q4 | English (simple phrasing) | Get beginner-friendly sources |
| Q5 | English (recent) | Get latest news/updates |

If the topic is inherently Israeli (local news, Israeli law, etc.) → weight Hebrew sources more.

---

## Rules

1. **Always cite sources** — no answer without at least 2 URLs. For competitive analysis: minimum 5 sources.
2. **Deep questions → decompose first** (Step 0). Simple facts → skip decomposition.
3. **Max ~400 words** — be concise, not exhaustive
3. **Direct answer first** — no preamble, no "I will now search..."
4. **Hebrew in, Hebrew out** — match the user's language
5. **Flag uncertainty** — if sources conflict or data is stale, say so
6. **No raw dumps** — synthesize, don't copy-paste snippets
7. **React 👍** when owner requests research, **✅** when delivered
8. After delivering research — write summary to `memory/whatsapp/dms/<PHONE-sanitized>/context.md` if topic was important

---

## Cost Notes

- 3–5 `web_search` calls per research request — moderate cost
- Avoid `web_fetch` unless snippets are truly insufficient
- For simple factual questions (capital cities, dates, etc.) → single search is enough, skip full synthesizer flow
- Cache: if the same topic was researched in the last hour, reuse results
