---
skill_name: cost-optimizer
version: "1.0.0"
category: optimization
trigger: auto
execution_mode: async
---

# Cost Optimizer

## Intent
Minimize API and infrastructure costs while maintaining quality.

## Optimization Strategies

### Model Selection
- Use cheapest adequate model
- Cache frequent queries
- Batch similar requests
- Compress prompts

### Token Efficiency
- Shorten system prompts
- Remove redundant context
- Use abbreviations internally
- Summarize long inputs

### Caching
- Cache identical requests
- Store frequent responses
- Use embeddings for similarity
- TTL-based cache expiration

### Batch Processing
- Group small tasks
- Process during off-peak
- Use batch APIs when available
- Parallelize independent tasks

### Infrastructure
- Auto-scale down during low load
- Use spot instances
- Optimize container sizes
- Right-size databases

## Budget Management
- Set daily/weekly/monthly budgets
- Alert at 50%, 80%, 100%
- Hard stop at 120%
- Track per-agent costs

## Rules
1. Never compromise quality for cost
2. Cache aggressively
3. Batch when possible
4. Monitor continuously
5. Alert before overspending

## Metrics
- Cost per task
- Cost per agent
- Daily spend
- Budget utilization
- Savings from optimization

## Example
```python
# Optimize agent configuration
optimized = await cost_optimizer.optimize_agent(agent)
# Returns: {"new_model": "llama-3.1-8b", "estimated_savings": "35%"}

# Get cost report
report = await cost_optimizer.get_report()
# Returns: {"daily_cost": 45.20, "budget": 100.00, "remaining": 54.80}
```
