---
skill_name: autonomous-continuation
version: "1.0.0"
category: fable5
trigger: auto
execution_mode: async
---

# Autonomous Continuation

## Intent
Enable unattended runs that don't stall on mid-run permission questions or "I'll now run X" statements.

## When to Apply
- Batch operations
- Long-running tasks
- Scheduled executions
- CI/CD pipelines

## Rules
1. NEVER say "I'll now run X" - just run it
2. NEVER ask for permission mid-task unless explicitly configured to do so
3. If a step fails, apply recovery strategy automatically
4. Report progress at natural checkpoints, not every action
5. Maintain context budget - summarize old context when needed

## Context Budget Pattern
- When context reaches 80% capacity, summarize previous work
- Keep: current task, recent errors, key decisions
- Archive: completed subtasks, old reasoning

## Recovery Strategies
- Timeout: increase timeout, switch to faster model
- Rate limit: exponential backoff
- API error: retry with fallback model
- Context overflow: summarize and truncate

## Example
Bad: "I'll now create the file. Should I proceed?"
Good: "[creates file] Done. Next: updating imports..."
