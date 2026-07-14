---
skill_name: skill-refactorer
version: "1.0.0"
category: fable5
trigger: auto
execution_mode: sync
---

# Skill Refactorer

## Intent
The meta-skill. Audit pre-Fable-5 skills/prompts, delete capability-compensation scaffolding, keep real guardrails.

## Audit Checklist
- [ ] Remove step-by-step recipes (Fable 5 follows intent)
- [ ] Remove "be careful" exhortations (use verification hooks)
- [ ] Remove capability-compensation (e.g., "think step by step")
- [ ] Keep real guardrails (boundaries, checks, constraints)
- [ ] Convert procedures to intent + boundaries
- [ ] Add verification hooks where correctness matters

## Patterns to Delete
1. "Think step by step" -> Fable 5 does this naturally
2. "Be very careful" -> Use verification instead
3. "First do X, then Y, then Z" -> State outcome, let Fable 5 figure out steps
4. "You are an expert..." -> Fable 5 doesn't need ego stroking
5. Long examples -> Fable 5 generalizes from brief examples

## Patterns to Keep
1. Boundaries: "Don't modify files outside src/"
2. Checks: "Verify output matches schema X"
3. Constraints: "Max 100 lines per function"
4. Verification: "Run tests before submitting"
5. Format requirements: "Output must be valid JSON"

## Example Transformation
Before:
```
You are an expert Python developer. Think step by step.
First, analyze the requirements. Then, design the solution.
Then, implement it carefully. Then, test it thoroughly.
Be very careful with edge cases.
```

After:
```
Implement feature X with these constraints:
- Don't modify files outside src/
- Output must pass existing tests
- Max 100 lines per function
- Verify: run pytest before submitting
```
