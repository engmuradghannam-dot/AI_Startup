from typing import Dict, Any, List, Optional

class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
    
    async def add_node(self, node_id: str, data: Dict[str, Any]) -> bool:
        self.nodes[node_id] = data
        return True
    
    async def add_edge(self, from_node: str, to_node: str, relation: str) -> bool:
        self.edges.append({
            "from": from_node,
            "to": to_node,
            "relation": relation
        })
        return True
    
    async def query(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self.nodes.get(node_id)
    
    async def get_related(self, node_id: str) -> List[Dict[str, Any]]:
        related = []
        for edge in self.edges:
            if edge["from"] == node_id or edge["to"] == node_id:
                related.append(edge)
        return related

# Singleton
_knowledge_graph = None

def get_knowledge_graph():
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph()
    return _knowledge_graph

def get_knowledge_graph_service():
    """Service accessor for knowledge graph"""
    return get_knowledge_graph()

knowledge_graph = get_knowledge_graph()
