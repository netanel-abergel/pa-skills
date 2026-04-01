---
name: spawn-subagent
description: "Spawn isolated subagents to handle long-running, complex, or blocking tasks without stalling the main session. Use when: a task will take more than 30 seconds, involves multiple sequential steps, requires heavy file processing, could block the main session, or when parallelism would speed things up. Prevents the main agent from getting stuck on slow operations."
---

# Spawn Subagent Skill

Delegate long or complex tasks to isolated subagents so the main session stays responsive.

---

## When to Spawn a Subagent

**Spawn when:**
- Task will take >30 seconds (file processing, API batch calls, code generation)
- Task involves many sequential steps (research → draft → send → log)
- Task could fail/loop and block the main session
- Multiple independent tasks can run in parallel
- Owner wants results "when ready" rather than waiting now

**Stay in main session when:**
- Task is a simple lookup or quick action (<10 seconds)
- Task requires back-and-forth with the owner
- Task needs access to the current conversation context

---

## How to Spawn (OpenClaw)

### Basic Spawn

```python
# Via sessions_spawn tool
sessions_spawn(
    task="[Detailed task description here]",
    mode="run",           # "run" = one-shot, "session" = persistent
    runtime="subagent",
    runTimeoutSeconds=300  # 5 min max; adjust as needed
)
```

### With Streaming Output

```python
# Stream output back to parent session (ACP only)
sessions_spawn(
    task="[Task]",
    mode="run",
    runtime="acp",
    agentId="your-agent-id",
    streamTo="parent"
)
```

---

## Task Description Best Practices

A good task description for a subagent includes:

1. **What to do** — specific, unambiguous instructions
2. **Where to find inputs** — file paths, API endpoints, environment variables
3. **What to output** — exact format, where to save results
4. **How to finish** — what "done" looks like

### Example: Good Task Description

```
Read all .md files in /tmp/reports/, 
summarize each one in 2–3 sentences,
save the combined summary to /tmp/reports/summary.md,
then print "DONE" to stdout.

Use the file paths exactly as given. Do not modify the original files.
```

### Example: Bad Task Description

```
Summarize the reports.
```
*(Too vague — subagent won't know where to find files or where to save output)*

---

## Common Subagent Patterns

### Pattern 1: Batch Processing

```python
# Spawn one subagent per batch item
for item in items:
    sessions_spawn(
        task=f"Process item: {item}. Save result to /tmp/results/{item}.json",
        mode="run",
        runtime="subagent",
        runTimeoutSeconds=120
    )
# Then wait for completion events
```

### Pattern 2: Research + Draft

```python
sessions_spawn(
    task="""
    1. Search the web for: [topic]
    2. Summarize the top 5 results in bullet points
    3. Draft a 3-paragraph briefing for a non-technical executive
    4. Save the draft to /tmp/briefing.md
    5. Print "DONE" when finished
    """,
    mode="run",
    runtime="subagent",
    runTimeoutSeconds=180
)
```

### Pattern 3: Long-Running Cron Task

```python
sessions_spawn(
    task="""
    This is a scheduled task.
    1. Check all PAs in data/pa-directory.json for billing errors
    2. For each PA with billing_error=true, send a WhatsApp alert to their owner
    3. Save a status report to /tmp/billing-status.json
    """,
    mode="run",
    runtime="subagent",
    runTimeoutSeconds=300
)
```

### Pattern 4: Parallel Independent Tasks

```python
# Spawn both at once — they run in parallel
sessions_spawn(task="Fetch latest emails and save to /tmp/emails.json", mode="run", runtime="subagent")
sessions_spawn(task="Get today's calendar events and save to /tmp/calendar.json", mode="run", runtime="subagent")
# Then wait for both to complete before combining results
```

---

## Handling Completion

After spawning, **do not poll**. Wait for the completion event to arrive as a message.

When the completion event arrives:
1. Read the output file(s) the subagent was asked to create
2. Use the results in the main session
3. Reply with NO_REPLY if no user response is needed

```
# Completion event looks like:
# "Subagent completed: [childSessionKey]"
# Then read the output:
result = read("/tmp/output.json")
```

---

## Timeout and Failure Handling

```python
sessions_spawn(
    task="[Task]",
    mode="run",
    runtime="subagent",
    runTimeoutSeconds=120  # Kill after 2 min if still running
)
```

If subagent times out or fails:
1. Log the failure: append to `.learnings/ERRORS.md`
2. Notify owner if task was time-sensitive
3. Retry with a simpler, more explicit task description
4. Fall back to running in main session if critical

---

## Anti-Patterns to Avoid

| ❌ Don't | ✅ Do Instead |
|---|---|
| Poll with sessions_list in a loop | Wait for push-based completion events |
| Spawn for a 5-second task | Run quick tasks in main session |
| Give vague task descriptions | Be explicit about inputs, outputs, and file paths |
| Spawn without a timeout | Always set runTimeoutSeconds |
| Ignore subagent failures | Check for error events and handle them |

---

## Model Notes

- Subagents inherit the same model as the parent unless overridden
- For heavy reasoning tasks (code generation, analysis), use a larger model
- For simple batch operations, a smaller/faster model saves cost

```python
sessions_spawn(
    task="[Complex analysis task]",
    mode="run",
    runtime="subagent",
    model="your-provider/your-model"  # Override model for this task
    # Examples: "anthropic/claude-opus-4-6", "openai/gpt-4o", "google/gemini-1.5-pro"
)
```

---

## Practical Example: PA Daily Briefing via Subagent

Instead of blocking the main session for 2 minutes:

```python
# In main session — fire and forget
sessions_spawn(
    task="""
    Generate the daily morning briefing for the owner:
    1. Get today's calendar events using: GOG_ACCOUNT=owner@company.com gog calendar events primary --from TODAY --to TOMORROW
    2. Get urgent emails: GOG_ACCOUNT=owner@company.com gog gmail search 'is:unread newer_than:1d' --max 5
    3. Format as a WhatsApp message (no markdown headers, use bold for sections)
    4. Save to /tmp/morning-briefing.txt
    5. Print DONE
    """,
    mode="run",
    runtime="subagent",
    runTimeoutSeconds=120
)
# Main session stays free. When done, read /tmp/morning-briefing.txt and send it.
```
