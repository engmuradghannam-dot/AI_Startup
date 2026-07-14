---
skill_name: error-recovery
version: "1.0.0"
category: orchestration
trigger: event
execution_mode: async
---

# Error Recovery

## Intent
Automatically recover from failures without human intervention.

## Error Types & Recovery

### Timeout
- Increase timeout (2x)
- Switch to faster model
- Split task into smaller chunks

### Rate Limit (429)
- Exponential backoff: wait 2^retry seconds
- Switch to alternative API key
- Queue for later processing

### Context Length
- Summarize context
- Remove old messages
- Use context compression

### API Error (5xx)
- Retry with exponential backoff
- Switch to fallback model
- Degrade gracefully (return partial results)

### Unknown Error
- Log full error details
- Retry with reduced parameters
- Escalate to human if max retries exceeded

## Rules
1. Max 3 retries per task
2. Log all recovery attempts
3. Never lose task data
4. Notify on unrecoverable errors
5. Update error statistics

## Self-Healing
- Reset agent state on repeated failures
- Clear short-term memory
- Restore default configuration
- Re-register with load balancer

## Example
```python
result = await agent.execute_task(task)
if not result.success:
    recovery = await error_recovery.handle_failure(task, agent, result.error)
    # Automatically retries with adjusted parameters
```
