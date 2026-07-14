---
skill_name: knowledge-graph
version: "1.0.0"
category: learning
trigger: auto
execution_mode: async
---

# Knowledge Graph

## Intent
Build and maintain a graph of interconnected knowledge for agents to reason over.

## Graph Structure

### Nodes
- Concepts: abstract ideas
- Entities: specific objects
- Agents: AI agents
- Skills: capabilities
- Tasks: work items
- Documents: source materials

### Edges
- is_a: type relationship
- part_of: composition
- related_to: association
- depends_on: dependency
- improves: enhancement
- contradicts: conflict

## Operations

### Construction
- Extract entities from text
- Identify relationships
- Assign confidence scores
- Merge duplicate nodes

### Querying
- Find related concepts
- Path finding
- Similarity search
- Subgraph extraction

### Maintenance
- Update confidence scores
- Remove outdated edges
- Merge similar nodes
- Archive old knowledge

### Reasoning
- Infer new relationships
- Detect contradictions
- Suggest connections
- Validate consistency

## Rules
1. Every edge must have evidence
2. Confidence scores reflect certainty
3. Source all knowledge
4. Version control changes
5. Regular maintenance required

## Example
```python
# Add knowledge
await knowledge_graph.add_node(
    node_id="python_async",
    node_type="concept",
    label="Python Async Programming",
    description="Asynchronous programming in Python using asyncio"
)

await knowledge_graph.add_edge(
    source="python_async",
    target="fastapi",
    relation="related_to",
    weight=0.9
)

# Query related concepts
related = await knowledge_graph.find_related("python_async", max_depth=2)
# Returns: [{"node_id": "fastapi", "relation": "related_to", "weight": 0.9}, ...]
```
