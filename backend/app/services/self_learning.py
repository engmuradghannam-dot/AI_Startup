"""Self-Learning and Improvement System.

Enables agents to learn from interactions, improve responses,
and adapt to user preferences over time.
"""
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from collections import defaultdict
import asyncio

from app.services.advanced_memory import get_memory_system, MemoryEntry
from app.models.memory import LearningPatternDoc


class LearningPattern:
    """A learned pattern from interactions."""

    def __init__(self, pattern_type: str, trigger: str, response: str,
                 confidence: float = 0.5, source: str = "interaction"):
        self.pattern_type = pattern_type  # preference, style, correction, enhancement
        self.trigger = trigger
        self.response = response
        self.confidence = confidence
        self.source = source
        self.created_at = datetime.utcnow()
        self.usage_count = 0
        self.success_rate = 0.5

    def to_dict(self) -> Dict:
        return {
            "pattern_type": self.pattern_type,
            "trigger": self.trigger,
            "response": self.response,
            "confidence": self.confidence,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
        }


class SelfLearningSystem:
    """System for agent self-learning and improvement."""

    def __init__(self):
        self.patterns: Dict[str, List[LearningPattern]] = defaultdict(list)
        self.feedback_history: Dict[str, List[Dict]] = defaultdict(list)
        self.performance_metrics: Dict[str, Dict] = defaultdict(lambda: {
            "total_interactions": 0,
            "successful_interactions": 0,
            "avg_response_time": 0,
            "user_satisfaction": 0.5,
            "improvement_rate": 0.0,
        })
        self.learning_queue: asyncio.Queue = asyncio.Queue()
        self.is_learning = False
        self._loaded_agents: set = set()

    async def _ensure_loaded(self, agent_id: str):
        """Load this agent's persisted patterns from MongoDB the first time it's
        touched this process, so learning survives a restart. No-ops without a DB."""
        if agent_id in self._loaded_agents:
            return
        self._loaded_agents.add(agent_id)
        try:
            docs = await LearningPatternDoc.find(LearningPatternDoc.agent_id == agent_id).to_list()
            for doc in docs:
                pattern = LearningPattern(
                    pattern_type=doc.pattern_type, trigger=doc.trigger, response=doc.response,
                    confidence=doc.confidence, source=doc.source,
                )
                pattern.created_at = doc.created_at
                pattern.usage_count = doc.usage_count
                pattern.success_rate = doc.success_rate
                self.patterns[agent_id].append(pattern)
        except Exception:
            pass

    async def record_interaction(self, agent_id: str, query: str,
                                response: str, feedback: Optional[Dict] = None):
        """Record an interaction for learning."""
        await self._ensure_loaded(agent_id)
        interaction = {
            "query": query,
            "response": response,
            "timestamp": datetime.utcnow().isoformat(),
            "feedback": feedback or {},
        }
        self.feedback_history[agent_id].append(interaction)

        # Update metrics
        metrics = self.performance_metrics[agent_id]
        metrics["total_interactions"] += 1

        if feedback:
            if feedback.get("rating", 0) >= 4:
                metrics["successful_interactions"] += 1

            # Update satisfaction
            ratings = [f.get("rating", 3) for f in 
                      [i["feedback"] for i in self.feedback_history[agent_id] if i["feedback"]]]
            if ratings:
                metrics["user_satisfaction"] = sum(ratings) / len(ratings) / 5.0

        # Add to learning queue
        await self.learning_queue.put({
            "agent_id": agent_id,
            "interaction": interaction,
        })

    async def _persist_pattern(self, agent_id: str, pattern: "LearningPattern"):
        """Best-effort persistence so a learned pattern survives a restart."""
        try:
            await LearningPatternDoc(
                agent_id=agent_id, pattern_type=pattern.pattern_type, trigger=pattern.trigger,
                response=pattern.response, confidence=pattern.confidence, source=pattern.source,
            ).insert()
        except Exception:
            pass

    async def learn_from_feedback(self, agent_id: str):
        """Learn from collected feedback."""
        await self._ensure_loaded(agent_id)
        history = self.feedback_history.get(agent_id, [])
        if len(history) < 5:
            return

        # Analyze recent interactions
        recent = history[-20:]

        # Extract patterns from positive feedback
        positive = [i for i in recent if i["feedback"].get("rating", 3) >= 4]
        negative = [i for i in recent if i["feedback"].get("rating", 3) <= 2]

        # Learn from positive examples
        for interaction in positive:
            pattern = LearningPattern(
                pattern_type="preference",
                trigger=interaction["query"][:100],
                response=interaction["response"][:200],
                confidence=0.7,
                source="positive_feedback"
            )
            self.patterns[agent_id].append(pattern)
            await self._persist_pattern(agent_id, pattern)

        # Learn from negative examples (what to avoid)
        for interaction in negative:
            pattern = LearningPattern(
                pattern_type="correction",
                trigger=interaction["query"][:100],
                response=interaction["feedback"].get("correction", ""),
                confidence=0.8,
                source="negative_feedback"
            )
            self.patterns[agent_id].append(pattern)
            await self._persist_pattern(agent_id, pattern)

        # Calculate improvement
        metrics = self.performance_metrics[agent_id]
        if metrics["total_interactions"] > 10:
            recent_success = len(positive) / len(recent) if recent else 0
            metrics["improvement_rate"] = recent_success - metrics["user_satisfaction"]

    async def get_relevant_patterns(self, agent_id: str, query: str, limit: int = 3) -> List[LearningPattern]:
        """Find learned patterns relevant to a query, best match first."""
        await self._ensure_loaded(agent_id)
        patterns = self.patterns.get(agent_id, [])

        relevant = []
        for pattern in patterns:
            # Simple keyword matching (can be enhanced with embeddings)
            if any(word in query.lower() for word in pattern.trigger.lower().split()):
                relevant.append(pattern)

        relevant.sort(key=lambda p: (p.confidence * p.success_rate), reverse=True)
        return relevant[:limit]

    async def get_improved_response(self, agent_id: str, query: str,
                                    base_response: str) -> Tuple[str, List[Dict]]:
        """Get an improved response based on learned patterns."""
        relevant = await self.get_relevant_patterns(agent_id, query, limit=3)
        if not relevant:
            return base_response, []

        # Apply top patterns
        improved = base_response
        applied_patterns = []

        for pattern in relevant:
            if pattern.pattern_type == "preference":
                # Enhance response with preferred style
                improved = await self._apply_style(improved, pattern.response)
                applied_patterns.append(pattern.to_dict())
            elif pattern.pattern_type == "correction":
                # Apply correction
                improved = await self._apply_correction(improved, pattern.response)
                applied_patterns.append(pattern.to_dict())

        return improved, applied_patterns

    async def _apply_style(self, response: str, style_example: str) -> str:
        """Apply learned style to response."""
        # In production, use LLM to rewrite with style
        # For now, append style note
        return response

    async def _apply_correction(self, response: str, correction: str) -> str:
        """Apply learned correction to response."""
        # In production, use LLM to apply correction
        return response

    async def get_learning_stats(self, agent_id: str) -> Dict:
        """Get learning statistics for an agent."""
        await self._ensure_loaded(agent_id)
        patterns = self.patterns.get(agent_id, [])
        history = self.feedback_history.get(agent_id, [])
        metrics = self.performance_metrics[agent_id]

        return {
            "total_patterns_learned": len(patterns),
            "pattern_types": {
                "preferences": len([p for p in patterns if p.pattern_type == "preference"]),
                "corrections": len([p for p in patterns if p.pattern_type == "correction"]),
                "enhancements": len([p for p in patterns if p.pattern_type == "enhancement"]),
            },
            "total_interactions": metrics["total_interactions"],
            "successful_interactions": metrics["successful_interactions"],
            "user_satisfaction": round(metrics["user_satisfaction"] * 100, 2),
            "improvement_rate": round(metrics["improvement_rate"] * 100, 2),
            "feedback_count": len([h for h in history if h["feedback"]]),
            "avg_confidence": round(
                sum(p.confidence for p in patterns) / len(patterns), 2
            ) if patterns else 0,
        }

    async def start_continuous_learning(self):
        """Start continuous learning loop."""
        self.is_learning = True
        while self.is_learning:
            try:
                item = await asyncio.wait_for(self.learning_queue.get(), timeout=5.0)
                agent_id = item["agent_id"]

                # Process learning for this agent
                if len(self.feedback_history[agent_id]) % 10 == 0:
                    await self.learn_from_feedback(agent_id)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Learning error: {e}")

    async def stop_continuous_learning(self):
        """Stop continuous learning."""
        self.is_learning = False

    async def export_knowledge(self, agent_id: str) -> Dict:
        """Export learned knowledge for an agent."""
        return {
            "patterns": [p.to_dict() for p in self.patterns.get(agent_id, [])],
            "metrics": self.performance_metrics[agent_id],
            "feedback_count": len(self.feedback_history.get(agent_id, [])),
        }

    async def import_knowledge(self, agent_id: str, knowledge: Dict):
        """Import learned knowledge for an agent."""
        for pattern_data in knowledge.get("patterns", []):
            pattern = LearningPattern(
                pattern_type=pattern_data["pattern_type"],
                trigger=pattern_data["trigger"],
                response=pattern_data["response"],
                confidence=pattern_data.get("confidence", 0.5),
                source=pattern_data.get("source", "imported")
            )
            self.patterns[agent_id].append(pattern)


# Singleton instance
_learning_system: Optional[SelfLearningSystem] = None


async def get_learning_system() -> SelfLearningSystem:
    """Get or create the learning system singleton."""
    global _learning_system
    if _learning_system is None:
        _learning_system = SelfLearningSystem()
    return _learning_system
