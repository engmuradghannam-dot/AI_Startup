---
skill_name: regrounding-summary
version: "1.0.0"
category: fable5
trigger: auto
execution_mode: sync
---

# Regrounding Summary

## Intent
Final reports readable by someone who saw none of the work - no arrow chains, no invented abbreviations.

## Rules
1. Write for someone who joined mid-project
2. No arrow chains: "A -> B -> C" -> "A leads to B, which causes C"
3. No invented abbreviations: spell out on first use
4. Include context: what was asked, what was done, why
5. State assumptions explicitly
6. Provide concrete evidence, not summaries of summaries

## Structure
```
## What Was Requested
[Clear restatement of original ask]

## What Was Done
[High-level summary of actions]

## Key Decisions
[Why certain approaches were chosen]

## Results
[Concrete outcomes with evidence]

## Next Steps
[Recommended follow-up actions]
```

## Anti-Patterns
- "As discussed..." -> Reader wasn't there
- "The usual approach..." -> Define what's usual
- "Fixed the thing" -> Specify what thing and how
- "It works now" -> Explain what "works" means

## Example
Bad: "Fixed the auth issue by updating the middleware."
Good: "Fixed the authentication timeout issue (users logged out after 5 minutes) by increasing JWT expiration from 300s to 3600s in auth/middleware.py. Verified: 10/10 test users remained logged in for 1 hour."
