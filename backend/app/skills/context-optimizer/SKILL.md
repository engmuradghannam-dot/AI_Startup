---
skill_name: context-optimizer
version: "1.0.0"
category: optimization
trigger: conditional
execution_mode: sync
---

# Context Optimizer

## Intent
Maximize effective context window usage by compressing, summarizing, and prioritizing content.

## Optimization Strategies

### Summarization
- Summarize old conversation turns
- Keep last N turns verbatim
- Compress system prompts

### Prioritization
- Rank messages by relevance
- Keep high-relevance content
- Archive low-relevance content

### Deduplication
- Remove duplicate system messages
- Merge similar user messages
- Eliminate redundant context

### Truncation
- Truncate long messages with ellipsis
- Preserve message structure
- Maintain semantic coherence

## Rules
1. Never lose critical information
2. Preserve message order
3. Maintain conversation flow
4. Compress only when > 80% capacity
5. Track compression ratio

## Metrics
- Original token count
- Optimized token count
- Compression ratio
- Information loss (estimated)

## Example
```python
# Before: 120K tokens (exceeds 128K limit)
# After optimization: 95K tokens
optimized = await context_optimizer.optimize(
    messages=conversation,
    max_tokens=128000,
    strategy="summarize_old"
)
```
