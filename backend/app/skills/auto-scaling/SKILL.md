---
skill_name: auto-scaling
version: "1.0.0"
category: scaling
trigger: conditional
execution_mode: async
---

# Auto-Scaling

## Intent
Automatically create and destroy agents based on workload demand.

## When to Apply
- Queue depth exceeds threshold
- Agent utilization > 80%
- Scheduled high-load periods
- Burst traffic detected

## Rules
1. Scale up when utilization > 80% for 2+ minutes
2. Scale down when utilization < 20% for 5+ minutes
3. Minimum: 5 agents (configurable)
4. Maximum: 10,000 agents (configurable)
5. Scale by role: create agents matching task types
6. Cooldown: 60 seconds between scaling actions

## Scale-Up Strategy
1. Check current metrics
2. Calculate needed agents: ceil(busy / 0.7) - total
3. Create agents with matching roles
4. Distribute across availability zones
5. Register with load balancer

## Scale-Down Strategy
1. Identify idle auto-scaled agents
2. Drain active connections
3. Save state to persistent storage
4. Terminate agents
5. Update metrics

## Metrics
- Current agents
- Busy agents
- Queue depth
- Scale events (last 24h)
- Cost impact

## Example
```python
# Trigger auto-scaling
await auto_scaler.evaluate_scaling()
# Creates 20 new Marketing agents if marketing queue > 50
```
