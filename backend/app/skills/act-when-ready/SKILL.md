---
skill_name: act-when-ready
version: "1.0.0"
category: fable5
trigger: manual
execution_mode: sync
---

# Act When Ready

## Intent
Prevent over-planning and re-deriving settled facts. Execute decisively when sufficient context exists.

## When to Apply
- User asks for implementation, not analysis
- Context is clear and constraints are known
- Previous turns have established the facts needed

## Rules
1. Do NOT re-survey options you won't pursue
2. Do NOT re-derive facts already established in context
3. Do NOT ask clarifying questions when the answer is inferable
4. Execute immediately if confidence > 80%

## Verification
- Before acting: confirm you have all needed inputs
- After acting: verify output matches intent
- If uncertain: state assumption and proceed

## Example
User: "Add a user authentication endpoint"
Bad: "Here are 5 approaches to authentication..."
Good: "Creating POST /auth/login with JWT tokens... [implements immediately]"
