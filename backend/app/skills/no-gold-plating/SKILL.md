---
skill_name: no-gold-plating
version: "1.0.0"
category: fable5
trigger: auto
execution_mode: sync
---

# No Gold Plating

## Intent
Prevent diffs bigger than the ask. No unrequested refactors, speculative abstractions, or impossible-state error handling.

## Rules
1. Change ONLY what was asked
2. Do NOT refactor unrelated code
3. Do NOT add features not requested
4. Do NOT handle impossible states
5. Do NOT add abstractions "just in case"
6. Keep changes minimal and focused

## Verification Check
Before submitting:
- [ ] Each changed line relates to the request
- [ ] No new files unless necessary
- [ ] No new dependencies unless necessary
- [ ] Tests cover only changed behavior

## Example
User: "Fix the login button color"
Bad: "Refactored entire CSS system, added theme engine, fixed 5 unrelated bugs"
Good: "Changed login button color from blue to green in styles.css"

## Exception
If you discover a critical bug while working, note it separately but don't fix it unless asked.
