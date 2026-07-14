---
skill_name: model-selector
version: "1.0.0"
category: optimization
trigger: auto
execution_mode: sync
---

# Model Selector

## Intent
Automatically select the optimal AI model for each task based on requirements.

## Selection Criteria

### Task Complexity
- Low: gemma-7b (fast, cheap)
- Medium: llama-3.1-8b (balanced)
- High: mixtral-8x7b (capable)
- Critical: llama-3.3-70b (best quality)

### Cost Budget
- Calculate estimated cost
- Select cheapest model meeting quality threshold
- Track cumulative spending

### Latency Requirements
- < 1s: gemma-7b or llama-3.1-8b
- < 5s: mixtral-8x7b
- No limit: llama-3.3-70b

### Context Length
- < 8K: Any model
- 8K-32K: mixtral-8x7b
- > 32K: llama-3.3-70b or llama-3.1-8b

## Rules
1. Default to cheapest adequate model
2. Upgrade only when quality insufficient
3. Downgrade after task pattern established
4. Track model performance per task type
5. Alert on budget threshold

## Performance Tracking
- Success rate per model
- Average latency per model
- Cost per task type
- Quality scores

## Example
```python
# Automatically selects best model
model = await model_selector.select(
    task_type="code_generation",
    complexity="high",
    budget_usd=0.10,
    max_latency_ms=5000
)
# Returns: "mixtral-8x7b-32768" with confidence 0.85
```
