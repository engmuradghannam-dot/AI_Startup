---
skill_name: code-evolver
version: "1.0.0"
category: learning
trigger: event
execution_mode: async
---

# Code Evolver

## Intent
Automatically analyze, optimize, and improve code quality.

## Capabilities
1. Static analysis (complexity, smells, bugs)
2. Performance optimization
3. Security hardening
4. Test generation
5. Documentation generation
6. Refactoring suggestions

## Analysis Dimensions

### Performance
- Time complexity
- Memory usage
- I/O patterns
- Caching opportunities

### Security
- SQL injection risks
- XSS vulnerabilities
- Secret leakage
- Input validation

### Maintainability
- Cyclomatic complexity
- Code duplication
- Function length
- Naming conventions

## Evolution Process
1. Analyze current code
2. Identify improvement opportunities
3. Generate optimized version
4. Verify equivalence (tests pass)
5. Measure improvement
6. Apply if improvement > threshold

## Rules
1. Never break existing functionality
2. All tests must pass after evolution
3. Document all changes
4. Rollback on regression
5. Respect code style guidelines

## Example
```python
# Before evolution
for i in range(len(items)):
    process(items[i])

# After evolution  
for item in items:
    process(item)
# Improvement: More Pythonic, better readability
```
