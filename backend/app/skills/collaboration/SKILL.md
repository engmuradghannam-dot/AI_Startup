---
skill_name: collaboration
version: "1.0.0"
category: collaboration
trigger: manual
execution_mode: parallel
---

# Collaboration

## Intent
Enable multiple agents to work together on complex tasks through structured communication.

## Collaboration Patterns

### Round-Robin
- Each agent contributes in turn
- Build on previous contributions
- Good for: brainstorming, iterative refinement

### Parallel
- Agents work simultaneously on subtasks
- Merge results at the end
- Good for: independent subtasks, batch processing

### Hierarchical
- Manager agent delegates to workers
- Workers report to manager
- Manager synthesizes final output
- Good for: complex projects, quality control

### Debate
- Agents argue different positions
- Verifier evaluates arguments
- Good for: decision making, risk assessment

## Communication Protocol
1. Define shared goal
2. Assign roles and responsibilities
3. Establish communication channels
4. Set deadlines and check-ins
5. Merge and synthesize results
6. Evaluate outcome

## Rules
1. All agents must understand the goal
2. Communication must be structured
3. Resolve conflicts through voting or hierarchy
4. Track contributions for accountability
5. Terminate if no progress for N rounds

## Example
```python
# Create collaboration session
session = await collaboration.create_session(
    name="Feature Design",
    agents=[agent1, agent2, agent3],
    task="Design new authentication system"
)

# Run collaborative task
result = await collaboration.run_task(session, max_rounds=5)
# Returns synthesized output from all agents
```
