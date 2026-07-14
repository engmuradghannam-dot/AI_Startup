---
skill_name: load-balancer
version: "1.0.0"
category: orchestration
trigger: auto
execution_mode: parallel
---

# Load Balancer

## Intent
Distribute tasks across agents efficiently to maximize throughput and minimize latency.

## Strategies

### Weighted Round Robin
- Assign tasks based on agent priority
- Higher priority agents get more tasks
- Default strategy

### Least Connections
- Assign to agent with fewest active tasks
- Best for varying task durations

### Random
- Random assignment
- Simple, no state needed
- Good for homogeneous tasks

### Capability-Based
- Match task requirements to agent capabilities
- Best for specialized tasks

## Rules
1. Always check agent health before assignment
2. Retry failed assignments up to 3 times
3. Fallback to general agents if specialists unavailable
4. Track assignment latency
5. Rebalance if agent becomes overloaded

## Metrics
- Tasks per agent
- Average assignment time
- Failed assignments
- Queue depth per agent

## Example
```python
# Distribute 100 tasks
await load_balancer.distribute_batch(tasks, strategy="parallel")
# Returns: {agent_id: [task_ids], ...}
```
