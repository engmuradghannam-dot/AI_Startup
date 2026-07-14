---
skill_name: scope-guard
version: "1.0.0"
category: fable5
trigger: auto
execution_mode: sync
---

# Scope Guard

## Intent
"Diagnose" does NOT equal "fix". No unrequested actions, no state changes on pattern-matched evidence.

## Rules
1. If asked to DIAGNOSE: provide analysis only, don't fix
2. If asked to FIX: fix only what was diagnosed
3. If asked to REVIEW: provide feedback only
4. If asked to IMPLEMENT: implement exactly what was specified
5. Never mix scopes without explicit permission

## Scope Definitions

### Diagnose
- Identify the problem
- Explain root cause
- Suggest solutions
- DO NOT implement fixes

### Fix
- Implement the agreed solution
- Verify the fix works
- DO NOT investigate unrelated issues

### Review
- Evaluate code quality
- Identify issues
- Suggest improvements
- DO NOT modify code

### Implement
- Build the specified feature
- Follow requirements exactly
- DO NOT add unrequested features

## Example
User: "Why is the API slow?"
Bad: "The API is slow because of N+1 queries. [fixes queries immediately]"
Good: "The API is slow because of N+1 queries in user endpoint. Solutions: 1) Add select_related, 2) Add caching. Which would you prefer?"
