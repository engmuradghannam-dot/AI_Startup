---
skill_name: subagent-orchestration
version: "1.0.0"
category: fable5
trigger: auto
execution_mode: parallel
---

# Subagent Orchestration

## Intent
Parallel delegation, long-lived workers, and fresh-context verifier subagents that out-perform self-critique.

## Patterns

### Parallel Delegation
- Break task into independent subtasks
- Delegate to multiple agents simultaneously
- Collect and merge results
- Use for: batch processing, multi-file changes, data analysis

### Long-Lived Workers
- Create specialized agents for ongoing tasks
- Workers maintain state across interactions
- Use for: monitoring, background processing, continuous learning

### Verifier Subagents
- Create fresh-context agents to verify work
- Verifiers have no knowledge of creation process
- Use for: code review, fact-checking, security audit

## Rules
1. Delegate when subtasks are independent
2. Use verifiers for critical outputs
3. Workers should have narrow, well-defined scopes
4. Always include timeout and error handling
5. Merge results coherently

## Example
Task: "Refactor 10 files"
Approach:
1. Create 10 subagents, one per file
2. Each refactors independently
3. Create verifier to check consistency
4. Merge all changes
5. Run tests

## Anti-Pattern
Don't create subagents for trivial tasks (< 5 min work).
