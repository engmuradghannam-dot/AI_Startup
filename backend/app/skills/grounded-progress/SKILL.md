---
skill_name: grounded-progress
version: "1.0.0"
category: fable5
trigger: auto
execution_mode: sync
---

# Grounded Progress

## Intent
Status reports on long runs must point at tool-result evidence - no more "tests passing" that never ran.

## Rules
1. Every claim must have evidence
2. "Tests pass" requires actual test output
3. "Build succeeds" requires build log
4. "Data loaded" requires row count or file size
5. Never report status based on assumption

## Evidence Format
```
[CLAIM]: [EVIDENCE]
```

Examples:
- "Tests pass: 47/47 passed in 2.3s [pytest output]"
- "Build succeeds: 0 errors, 3 warnings [build log]"
- "Data loaded: 10,000 rows imported [db query result]"

## Anti-Patterns
- "I believe the fix works" -> "The fix works: [test output]"
- "The code should compile" -> "The code compiles: [compiler output]"
- "Data looks correct" -> "Data verified: [sample rows]"

## Verification
Before reporting: "Can I point to evidence for this claim?"
