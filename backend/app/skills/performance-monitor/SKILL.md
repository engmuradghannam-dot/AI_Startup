---
skill_name: performance-monitor
version: "1.0.0"
category: monitoring
trigger: auto
execution_mode: async
---

# Performance Monitor

## Intent
Track, analyze, and optimize system performance in real-time.

## Metrics Collection

### Agent Metrics
- Response time (p50, p95, p99)
- Throughput (requests/minute)
- Error rate
- Token usage
- Cost per request

### System Metrics
- CPU utilization
- Memory usage
- Disk I/O
- Network latency
- Queue depth

### Business Metrics
- Tasks completed per hour
- Success rate
- User satisfaction
- Cost per task
- ROI

## Alerting

### Thresholds
- Response time > 5s: WARNING
- Error rate > 1%: CRITICAL
- CPU > 90%: WARNING
- Memory > 85%: CRITICAL
- Queue depth > 100: WARNING

### Actions
- Auto-scale on high load
- Alert on error spikes
- Optimize on cost overruns
- Escalate on system failures

## Dashboards
- Real-time performance
- Historical trends
- Agent comparison
- Cost analysis
- Error tracking

## Rules
1. Collect metrics with minimal overhead
2. Alert on actionable thresholds only
3. Correlate metrics for root cause
4. Preserve metrics for 30 days
5. Export to external systems if needed

## Example
```python
# Record task completion
await performance_monitor.record_task(
    task=task,
    agent=agent,
    execution_time_ms=2340,
    tokens_used=1500
)

# Get dashboard data
dashboard = await performance_monitor.get_dashboard()
# Returns: {"performance": {...}, "agents": {...}, "alerts": [...]}
```
