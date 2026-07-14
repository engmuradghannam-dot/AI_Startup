---
skill_name: feedback-loop
version: "1.0.0"
category: learning
trigger: event
execution_mode: async
---

# Feedback Loop

## Intent
Continuously improve agent performance through feedback collection and learning.

## Feedback Types

### Explicit Feedback
- User ratings (1-5 stars)
- Written comments
- Correction suggestions
- Approval/rejection

### Implicit Feedback
- Task completion time
- Retry counts
- Error rates
- User engagement

### Comparative Feedback
- A/B test results
- Preference rankings
- Side-by-side comparisons

## Learning Process

### Collection
- Capture feedback after each interaction
- Store with full context
- Tag with metadata

### Analysis
- Aggregate by agent, skill, task type
- Identify patterns
- Detect degradation

### Improvement
- Update prompts based on feedback
- Adjust agent parameters
- Retrain on corrected examples
- Share learnings across agents

### Verification
- Test improvements
- Measure impact
- Rollback if regression
- Document changes

## Rules
1. Make feedback easy to give
2. Act on feedback promptly
3. Share learnings across agents
4. Measure improvement quantitatively
5. Respect user privacy

## Metrics
- Feedback collection rate
- Average rating per agent
- Improvement velocity
- Regression rate
- User satisfaction trend

## Example
```python
# Submit feedback
feedback = await feedback_loop.submit(
    agent_id=agent.id,
    task_id=task.id,
    rating=4,
    comment="Good but could be faster",
    expected_output="Detailed report",
    actual_output=result
)

# Process pending feedback
improvements = await feedback_loop.process_batch(limit=100)
# Returns: {"processed": 100, "improvements_applied": 15}
```
