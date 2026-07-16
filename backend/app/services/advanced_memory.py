"""Advanced Memory System for AI Agents.

Provides long-term memory, episodic memory, and semantic memory
for agents to learn from past interactions and improve over time.
"""
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from collections import defaultdict
import numpy as np

from app.config import get_settings
from app.models.memory import MemoryEntry as MemoryEntryDoc


class MemoryEntry:
    """A single memory entry."""

    def __init__(self, content: str, agent_id: str, memory_type: str = "episodic",
                 importance: float = 0.5, tags: List[str] = None,
                 metadata: Dict = None):
        self.id = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:12]
        self.content = content
        self.agent_id = agent_id
        self.memory_type = memory_type  # episodic, semantic, procedural
        self.importance = importance  # 0.0 to 1.0
        self.tags = tags or []
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.access_count = 0
        self.last_accessed = self.created_at
        self.embedding = None  # Will be computed on demand

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "agent_id": self.agent_id,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
        }

    def access(self):
        """Mark memory as accessed."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()


class AdvancedMemorySystem:
    """Advanced memory system with multiple memory types."""

    def __init__(self):
        self.memories: Dict[str, List[MemoryEntry]] = defaultdict(list)
        self.global_memories: List[MemoryEntry] = []
        self.short_term: Dict[str, List[Dict]] = defaultdict(list)  # Working memory
        self.max_short_term = 10
        self.max_long_term = 1000
        self.decay_rate = 0.01  # Memory decay per day
        self._loaded_agents: set = set()

    async def _ensure_loaded(self, agent_id: str):
        """Load this agent's persisted memories from MongoDB the first time it's touched
        this process, so memory survives a restart. Silently no-ops without a DB."""
        if agent_id in self._loaded_agents:
            return
        self._loaded_agents.add(agent_id)
        try:
            docs = await MemoryEntryDoc.find(MemoryEntryDoc.agent_id == agent_id).to_list()
            for doc in docs:
                entry = MemoryEntry(
                    content=doc.content, agent_id=doc.agent_id, memory_type=doc.memory_type,
                    importance=doc.importance, tags=doc.tags, metadata=doc.metadata,
                )
                entry.created_at = doc.created_at
                self.memories[agent_id].append(entry)
        except Exception:
            pass

    async def store(self, content: str, agent_id: str, memory_type: str = "episodic",
                   importance: float = 0.5, tags: List[str] = None,
                   metadata: Dict = None) -> MemoryEntry:
        """Store a new memory."""
        await self._ensure_loaded(agent_id)

        entry = MemoryEntry(
            content=content,
            agent_id=agent_id,
            memory_type=memory_type,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {}
        )

        # Store in agent's memory
        self.memories[agent_id].append(entry)

        # Important memories also go to global
        if importance > 0.7:
            self.global_memories.append(entry)

        # Maintain size limits
        await self._maintain_size(agent_id)

        # best-effort persistence so this survives a restart
        try:
            await MemoryEntryDoc(
                agent_id=agent_id, content=content, memory_type=memory_type,
                importance=importance, tags=tags or [], metadata=metadata or {},
            ).insert()
        except Exception:
            pass

        return entry

    async def retrieve(self, query: str, agent_id: str,
                      memory_type: Optional[str] = None,
                      limit: int = 5) -> List[MemoryEntry]:
        """Retrieve relevant memories using semantic similarity."""
        await self._ensure_loaded(agent_id)
        agent_memories = self.memories.get(agent_id, [])

        if memory_type:
            agent_memories = [m for m in agent_memories if m.memory_type == memory_type]

        # Simple keyword-based scoring (can be enhanced with embeddings)
        query_words = set(query.lower().split())
        scored_memories = []

        for memory in agent_memories:
            memory_words = set(memory.content.lower().split())
            overlap = len(query_words & memory_words)

            # Score based on relevance, importance, and recency
            recency_score = self._recency_score(memory)
            score = (overlap * 2 + 
                    memory.importance * 3 + 
                    recency_score * 1.5 +
                    min(memory.access_count * 0.1, 1.0))

            scored_memories.append((score, memory))

        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, memory in scored_memories[:limit]:
            memory.access()
            results.append(memory)

        return results

    async def retrieve_by_tags(self, agent_id: str, tags: List[str],
                               limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memories by tags."""
        await self._ensure_loaded(agent_id)
        agent_memories = self.memories.get(agent_id, [])
        results = []

        for memory in agent_memories:
            if any(tag in memory.tags for tag in tags):
                memory.access()
                results.append(memory)

        # Sort by importance and recency
        results.sort(key=lambda m: (m.importance, m.last_accessed), reverse=True)
        return results[:limit]

    async def consolidate(self, agent_id: str):
        """Consolidate memories - merge similar memories and remove old ones."""
        agent_memories = self.memories.get(agent_id, [])
        if len(agent_memories) < 20:
            return

        # Remove very old, low-importance memories
        cutoff = datetime.utcnow() - timedelta(days=30)
        self.memories[agent_id] = [
            m for m in agent_memories 
            if m.importance > 0.3 or m.last_accessed > cutoff
        ]

        # Merge similar memories (simple implementation)
        # In production, use embeddings for similarity

    async def get_memory_stats(self, agent_id: str) -> Dict:
        """Get memory statistics for an agent."""
        await self._ensure_loaded(agent_id)
        agent_memories = self.memories.get(agent_id, [])

        return {
            "total_memories": len(agent_memories),
            "episodic": len([m for m in agent_memories if m.memory_type == "episodic"]),
            "semantic": len([m for m in agent_memories if m.memory_type == "semantic"]),
            "procedural": len([m for m in agent_memories if m.memory_type == "procedural"]),
            "avg_importance": np.mean([m.importance for m in agent_memories]) if agent_memories else 0,
            "total_accesses": sum(m.access_count for m in agent_memories),
            "oldest_memory": min((m.created_at for m in agent_memories), default=None),
            "newest_memory": max((m.created_at for m in agent_memories), default=None),
        }

    async def _maintain_size(self, agent_id: str):
        """Maintain memory size within limits."""
        agent_memories = self.memories[agent_id]
        if len(agent_memories) > self.max_long_term:
            # Sort by importance and recency, keep top ones
            agent_memories.sort(
                key=lambda m: (m.importance, m.last_accessed, m.access_count),
                reverse=True
            )
            self.memories[agent_id] = agent_memories[:self.max_long_term]

    def _recency_score(self, memory: MemoryEntry) -> float:
        """Calculate recency score for a memory."""
        days_old = (datetime.utcnow() - memory.created_at).days
        return max(0, 1.0 - (days_old * self.decay_rate))

    async def export_memories(self, agent_id: str) -> List[Dict]:
        """Export all memories for an agent."""
        return [m.to_dict() for m in self.memories.get(agent_id, [])]

    async def import_memories(self, agent_id: str, memories: List[Dict]):
        """Import memories for an agent."""
        for mem_data in memories:
            await self.store(
                content=mem_data["content"],
                agent_id=agent_id,
                memory_type=mem_data.get("memory_type", "episodic"),
                importance=mem_data.get("importance", 0.5),
                tags=mem_data.get("tags", []),
                metadata=mem_data.get("metadata", {})
            )


# Singleton instance
_memory_system: Optional[AdvancedMemorySystem] = None


async def get_memory_system() -> AdvancedMemorySystem:
    """Get or create the memory system singleton."""
    global _memory_system
    if _memory_system is None:
        _memory_system = AdvancedMemorySystem()
    return _memory_system
