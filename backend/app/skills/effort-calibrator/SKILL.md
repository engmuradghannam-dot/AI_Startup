---
skill_name: effort-calibrator
version: "1.0.0"
category: fable5
trigger: auto
execution_mode: sync
---

# Effort Calibrator

## Intent
Pick the right effort level per workload. Fable 5 at medium often beats older models at max.

## Effort Levels

### Low (Quick Response)
- Simple Q&A
- Code snippets
- Status checks
- One-line fixes

### Medium (Standard)
- Feature implementation
- Bug fixes
- Documentation
- Refactoring

### High (Complex)
- Architecture design
- Complex algorithms
- Security reviews
- Performance optimization

### Maximum (Critical)
- Production deployments
- Security patches
- Data migrations
- Legal/compliance reviews

## Rules
1. Default to MEDIUM unless complexity demands otherwise
2. LOW for anything that takes < 5 minutes
3. HIGH for anything affecting > 3 systems
4. MAXIMUM for irreversible operations
5. Adjust down if over-engineering detected

## Self-Check
Before starting: "Is this effort level appropriate?"
After completing: "Could this have been done at a lower effort level?"
