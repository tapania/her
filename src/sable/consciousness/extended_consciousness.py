"""
Extended Consciousness: The Autobiographical Self

Implements Damasio's extended consciousness - awareness of past and future,
identity, and the narrative self.

Extended consciousness builds on core consciousness by adding:
1. Autobiographical memory - personal history with emotional coloring
2. Narrative self - the story we tell about who we are
3. Identity - stable traits that define us
4. Temporal extension - awareness of our continuity through time

This is what makes us feel like a continuous person with a history and future.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
from pathlib import Path

from sable.models.memory import Memory, Event, SomaticMarker
from sable.models.emotion import EmotionType
from sable.database.queries import (
    save_event,
    save_memory,
    query_memories,
    update_memory,
    get_event,
)


class ExtendedConsciousness:
    """
    Extended consciousness: Autobiographical memory and narrative self.

    This layer creates the sense of being a continuous person with
    a personal history and future.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize extended consciousness.

        Args:
            db_path: Path to database (optional)
        """
        self.db_path = db_path
        self.identity_traits: Dict[str, float] = {}  # Trait name -> strength (0-1)
        self.core_values: List[str] = []
        self.significant_memories: List[Memory] = []

    async def initialize(self, identity_traits: Optional[Dict[str, float]] = None) -> None:
        """
        Initialize extended consciousness with identity traits.

        Args:
            identity_traits: Dict of trait name -> strength
                           e.g., {'curiosity': 0.8, 'skepticism': 0.7}
        """
        if identity_traits:
            self.identity_traits = identity_traits

        # Load most significant memories
        self.significant_memories = await query_memories(
            min_salience=0.6,
            limit=20,
            db_path=self.db_path
        )

    async def record_event(
        self,
        description: str,
        context: Optional[str] = None,
        emotional_impact: Optional[Dict[str, float]] = None
    ) -> Event:
        """
        Record an event (something that happened).

        Not all events become memories - only emotionally salient ones.

        Args:
            description: What happened
            context: Additional context
            emotional_impact: Dict of emotion_type -> intensity

        Returns:
            The recorded Event
        """
        event = Event(
            description=description,
            context=context,
            timestamp=datetime.now(),
            emotional_impact=emotional_impact or {},
        )

        # Save to database
        event_id = await save_event(event, self.db_path)
        event.id = event_id

        return event

    async def encode_memory(
        self,
        event: Event,
        narrative_role: Optional[str] = None,
        identity_relevance: float = 0.5
    ) -> Optional[Memory]:
        """
        Encode an event into autobiographical memory.

        Only emotionally salient events become memories.
        The more intense the emotion, the stronger the memory.

        Args:
            event: The event to encode
            narrative_role: How this fits in life story (e.g., 'turning point')
            identity_relevance: How relevant to sense of self (0-1)

        Returns:
            Memory if salient enough, None otherwise
        """
        # Calculate emotional salience
        salience = event.get_emotional_salience()

        # Threshold: Only encode sufficiently salient events
        if salience < 0.3:
            return None

        # Extract emotion types from emotional impact
        associated_emotions = [
            emotion_type for emotion_type in event.emotional_impact.keys()
        ]

        # Create memory
        memory = Memory(
            event=event,
            emotional_salience=salience,
            consolidation_level=salience * 0.5,  # Initial consolidation based on salience
            narrative_role=narrative_role,
            associated_emotions=associated_emotions,
            identity_relevance=identity_relevance,
            created_at=datetime.now(),
        )

        # Save to database
        memory_id = await save_memory(memory, self.db_path)
        memory.id = memory_id

        # Add to significant memories if salient enough
        if salience >= 0.6:
            self.significant_memories.append(memory)
            # Keep only top 20
            self.significant_memories.sort(
                key=lambda m: m.emotional_salience,
                reverse=True
            )
            self.significant_memories = self.significant_memories[:20]

        return memory

    async def retrieve_memory(self, memory_id: int) -> Optional[Memory]:
        """
        Retrieve a specific memory by ID.

        Each retrieval strengthens the memory (consolidation).
        This simulates how remembering reinforces memories.

        Args:
            memory_id: Memory ID

        Returns:
            The Memory if found
        """
        # Find in significant memories cache
        for memory in self.significant_memories:
            if memory.id == memory_id:
                # Access the memory (strengthens it)
                updated_memory = memory.access()

                # Update in database
                await update_memory(updated_memory, self.db_path)

                # Update in cache
                idx = self.significant_memories.index(memory)
                self.significant_memories[idx] = updated_memory

                return updated_memory

        # Not in cache, query database
        # (Would need to implement get_memory_by_id in queries.py)
        return None

    async def query_memories_by_emotion(
        self,
        emotion_type: str,
        min_salience: float = 0.4
    ) -> List[Memory]:
        """
        Query memories associated with a specific emotion.

        Useful for understanding emotional patterns and history.

        Args:
            emotion_type: Type of emotion (e.g., 'fear', 'joy')
            min_salience: Minimum salience threshold

        Returns:
            List of matching memories
        """
        memories = await query_memories(
            min_salience=min_salience,
            limit=50,
            db_path=self.db_path
        )

        # Filter by emotion
        return [
            m for m in memories
            if emotion_type in m.associated_emotions
        ]

    async def get_identity_relevant_memories(self, min_relevance: float = 0.7) -> List[Memory]:
        """
        Get memories most relevant to sense of identity.

        These are the experiences that define who you are.

        Args:
            min_relevance: Minimum identity relevance

        Returns:
            List of identity-defining memories
        """
        memories = await query_memories(
            min_identity_relevance=min_relevance,
            limit=30,
            db_path=self.db_path
        )

        return memories

    def construct_narrative(self, memories: List[Memory]) -> str:
        """
        Construct a narrative from a set of memories.

        This simulates how we tell stories about ourselves - connecting
        memories into coherent narratives that define who we are.

        Args:
            memories: List of memories to weave into narrative

        Returns:
            Narrative text
        """
        if not memories:
            return "No significant memories to form a narrative."

        # Sort by timestamp
        sorted_memories = sorted(memories, key=lambda m: m.event.timestamp)

        # Build narrative
        narrative_parts = []

        for memory in sorted_memories:
            # Memory description
            desc = memory.event.description

            # Add emotional coloring
            if memory.associated_emotions:
                emotions_str = ", ".join(memory.associated_emotions)
                desc = f"{desc} (felt: {emotions_str})"

            # Add narrative role if present
            if memory.narrative_role:
                desc = f"[{memory.narrative_role}] {desc}"

            narrative_parts.append(desc)

        return "\n".join(narrative_parts)

    def update_identity_trait(self, trait_name: str, change: float) -> None:
        """
        Update an identity trait.

        Identity evolves slowly through experience.
        Significant experiences can shift traits.

        Args:
            trait_name: Name of trait (e.g., 'openness', 'cautiousness')
            change: How much to change (-1 to +1)
        """
        current = self.identity_traits.get(trait_name, 0.5)
        new_value = max(0.0, min(1.0, current + change))
        self.identity_traits[trait_name] = new_value

    def get_identity_profile(self) -> Dict[str, float]:
        """
        Get complete identity profile.

        Returns:
            Dict of trait -> strength
        """
        return self.identity_traits.copy()

    async def decay_memories(self, days_elapsed: float = 1.0) -> List[Memory]:
        """
        Apply decay to all memories.

        Memories fade over time without rehearsal.
        High-salience and well-consolidated memories decay slower.

        Args:
            days_elapsed: Days since last decay

        Returns:
            List of updated memories
        """
        updated_memories = []

        for memory in self.significant_memories:
            decay_factor = memory.decay_over_time(days_elapsed)

            # Apply decay to consolidation
            new_consolidation = memory.consolidation_level * decay_factor

            # Don't let it drop too low for very salient memories
            min_consolidation = memory.emotional_salience * 0.3
            new_consolidation = max(min_consolidation, new_consolidation)

            # Update memory
            memory.consolidation_level = new_consolidation

            # Update in database
            await update_memory(memory, self.db_path)

            updated_memories.append(memory)

        return updated_memories

    def to_dict(self) -> dict:
        """
        Export extended consciousness state as dictionary.

        Returns:
            Dict representation
        """
        return {
            'identity_traits': self.identity_traits,
            'core_values': self.core_values,
            'num_significant_memories': len(self.significant_memories),
            'most_recent_memories': [
                {
                    'description': m.event.description,
                    'salience': m.emotional_salience,
                    'emotions': m.associated_emotions,
                }
                for m in self.significant_memories[:5]
            ],
        }
