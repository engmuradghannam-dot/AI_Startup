---
skill_name: markdown-memory
version: "1.0.0"
category: fable5
trigger: auto
execution_mode: sync
---

# Markdown Memory

## Intent
A file-based lesson memory Fable 5 exploits unusually well - with the maintenance discipline that keeps it useful.

## Structure
```markdown
# Lesson: [Brief Title]

## Context
When/where this lesson applies

## Lesson
What was learned

## Evidence
Concrete examples, outputs, links

## Tags
#category #subcategory

## Date
YYYY-MM-DD
```

## Rules
1. Write lessons in markdown, not code
2. Include concrete evidence, not vague advice
3. Tag for discoverability
4. Review monthly - archive outdated lessons
5. Keep lessons atomic (one concept per file)

## Maintenance Discipline
- Monthly review: remove outdated lessons
- Consolidate: merge related lessons
- Archive: move old lessons to archive/
- Index: maintain an index.md for navigation

## When to Write
- After fixing a tricky bug
- After discovering a pattern
- After a failed approach
- After a successful optimization

## When NOT to Write
- Trivial discoveries
- Already documented patterns
- Hypothetical scenarios
