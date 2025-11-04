"""
State Manager: Main API for Sable's Consciousness System

The StateManager coordinates all three levels of consciousness:
- Proto-self (body state)
- Core consciousness (emotions, feelings)
- Extended consciousness (memory, narrative)

It also handles automatic time-based decay and state persistence.
"""

from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
from pydantic import BaseModel

from sable.consciousness.proto_self import ProtoSelf
from sable.consciousness.core_consciousness import CoreConsciousness
from sable.consciousness.extended_consciousness import ExtendedConsciousness
from sable.models.body_state import BodyState
from sable.models.emotion import Emotion, EmotionType, Feeling
from sable.models.memory import Memory, Event, SomaticMarker
from sable.database.schema import init_database


class ConsciousnessState(BaseModel):
    """
    Complete snapshot of consciousness state.

    Combines all three levels into a single coherent representation.
    """
    # Proto-self
    body_state: BodyState
    homeostatic_pressure: float
    background_emotion: str

    # Core consciousness
    active_emotions: List[Dict]
    emotional_state: Dict[str, float]
    overall_valence: float
    overall_arousal: float

    # Extended consciousness
    identity_traits: Dict[str, float]
    num_significant_memories: int

    # Metadata
    timestamp: datetime

    class Config:
        arbitrary_types_allowed = True


class StateManager:
    """
    Main interface to Sable's consciousness system.

    Coordinates all three consciousness layers and manages state evolution.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize state manager.

        Args:
            db_path: Path to database file (optional)
        """
        self.db_path = db_path
        self.proto_self = ProtoSelf(db_path)
        self.core_consciousness = CoreConsciousness(db_path)
        self.extended_consciousness = ExtendedConsciousness(db_path)
        self.initialized = False

    async def initialize(
        self,
        identity_traits: Optional[Dict[str, float]] = None,
        force_reset: bool = False
    ) -> None:
        """
        Initialize consciousness system.

        Creates database if needed and loads state.

        Args:
            identity_traits: Initial identity traits (for first-time setup)
            force_reset: Reset database (WARNING: deletes all data)
        """
        # Initialize database
        if force_reset:
            from sable.database.schema import reset_database
            await reset_database(self.db_path)
        else:
            await init_database(self.db_path)

        # Initialize all layers
        await self.proto_self.initialize()
        await self.core_consciousness.initialize()
        await self.extended_consciousness.initialize(identity_traits)

        self.initialized = True

    async def get_current_state(self) -> ConsciousnessState:
        """
        Get complete current consciousness state.

        Automatically applies time-based decay before returning state.

        Returns:
            ConsciousnessState with all levels
        """
        if not self.initialized:
            await self.initialize()

        # Apply automatic decay first
        await self.apply_automatic_decay()

        # Gather state from all layers
        body_state = await self.proto_self.get_state()
        homeostatic_pressure = self.proto_self.get_homeostatic_pressure()
        background_emotion = self.proto_self.get_background_emotion()

        valence, arousal = self.core_consciousness.get_overall_valence_arousal()

        return ConsciousnessState(
            body_state=body_state,
            homeostatic_pressure=homeostatic_pressure,
            background_emotion=background_emotion,
            active_emotions=self.core_consciousness.to_dict()['active_emotions'],
            emotional_state=self.core_consciousness.get_current_emotional_state(),
            overall_valence=valence,
            overall_arousal=arousal,
            identity_traits=self.extended_consciousness.identity_traits,
            num_significant_memories=len(self.extended_consciousness.significant_memories),
            timestamp=datetime.now(),
        )

    async def add_emotion(
        self,
        emotion_type: EmotionType,
        intensity: float,
        cause: str,
        create_feeling: bool = True
    ) -> Emotion:
        """
        Add an emotional event.

        This triggers both the emotion (body state change) and optionally
        the conscious feeling of that emotion.

        Args:
            emotion_type: Type of emotion
            intensity: Intensity (0-1)
            cause: What caused this emotion
            create_feeling: Whether to create conscious feeling (default True)

        Returns:
            The created Emotion
        """
        if not self.initialized:
            await self.initialize()

        # Get current body state
        body_state = await self.proto_self.get_state()

        # Trigger emotion
        emotion = await self.core_consciousness.trigger_emotion(
            emotion_type=emotion_type,
            intensity=intensity,
            cause=cause,
            body_state=body_state
        )

        # Apply body changes from emotion
        if emotion.body_signature:
            await self.proto_self.apply_body_changes(emotion.body_signature)

        # Create feeling if requested
        if create_feeling:
            await self.core_consciousness.feel_emotion(emotion)

        return emotion

    async def add_event(
        self,
        description: str,
        context: Optional[str] = None,
        emotional_impact: Optional[Dict[str, float]] = None,
        encode_as_memory: bool = True,
        narrative_role: Optional[str] = None
    ) -> Event:
        """
        Record an event (something that happened).

        Optionally encodes into autobiographical memory if emotionally salient.

        Args:
            description: What happened
            context: Additional context
            emotional_impact: Dict of emotion_type -> intensity
            encode_as_memory: Whether to try encoding as memory
            narrative_role: Role in life story

        Returns:
            The recorded Event
        """
        if not self.initialized:
            await self.initialize()

        # Record event
        event = await self.extended_consciousness.record_event(
            description=description,
            context=context,
            emotional_impact=emotional_impact
        )

        # Encode as memory if requested and salient enough
        if encode_as_memory:
            memory = await self.extended_consciousness.encode_memory(
                event=event,
                narrative_role=narrative_role
            )

            # If memory was created and has origin, potentially create somatic marker
            if memory and emotional_impact:
                await self._maybe_create_somatic_marker(memory, emotional_impact)

        # Trigger emotions from emotional impact
        if emotional_impact:
            for emotion_type_str, intensity in emotional_impact.items():
                try:
                    emotion_type = EmotionType(emotion_type_str)
                    await self.add_emotion(
                        emotion_type=emotion_type,
                        intensity=intensity,
                        cause=description
                    )
                except ValueError:
                    # Invalid emotion type, skip
                    pass

        return event

    async def query_memories(
        self,
        min_salience: float = 0.4,
        emotion_type: Optional[str] = None
    ) -> List[Memory]:
        """
        Query autobiographical memories.

        Args:
            min_salience: Minimum emotional salience
            emotion_type: Filter by emotion type (optional)

        Returns:
            List of matching memories
        """
        if not self.initialized:
            await self.initialize()

        if emotion_type:
            return await self.extended_consciousness.query_memories_by_emotion(
                emotion_type=emotion_type,
                min_salience=min_salience
            )
        else:
            from sable.database.queries import query_memories
            return await query_memories(
                min_salience=min_salience,
                db_path=self.db_path
            )

    async def get_somatic_marker(
        self,
        situation: str,
        min_strength: float = 0.3
    ) -> Optional[SomaticMarker]:
        """
        Get gut feeling (somatic marker) for a situation.

        Args:
            situation: Description of situation
            min_strength: Minimum marker strength

        Returns:
            Strongest matching somatic marker, or None
        """
        if not self.initialized:
            await self.initialize()

        return await self.core_consciousness.get_somatic_marker_for_situation(
            situation_description=situation,
            min_strength=min_strength
        )

    async def apply_automatic_decay(self) -> None:
        """
        Apply time-based decay to all consciousness components.

        Called automatically when getting state.
        """
        # Apply body state decay
        await self.proto_self.apply_decay()

        # Apply emotion decay
        await self.core_consciousness.apply_decay()

    async def _maybe_create_somatic_marker(
        self,
        memory: Memory,
        emotional_impact: Dict[str, float]
    ) -> None:
        """
        Potentially create a somatic marker from a significant memory.

        Somatic markers are formed from emotionally significant experiences.
        """
        # Only create markers for highly salient memories
        if memory.emotional_salience < 0.7:
            return

        # Extract primary emotion
        if not emotional_impact:
            return

        primary_emotion_type = max(emotional_impact.items(), key=lambda x: x[1])[0]

        try:
            emotion_type = EmotionType(primary_emotion_type)
        except ValueError:
            return

        # Determine valence from emotion
        valence = Emotion.get_default_valence(emotion_type)

        # Create somatic marker
        # Situation pattern is a simplified version of event description
        situation_pattern = memory.event.description[:50]  # First 50 chars

        await self.core_consciousness.create_somatic_marker(
            situation_pattern=situation_pattern,
            emotion_type=emotion_type,
            valence=valence,
            strength=memory.emotional_salience,
            origin_memory_id=memory.id
        )

    def to_dict(self) -> dict:
        """
        Export complete consciousness state as dictionary.

        Returns:
            Dict with all three levels
        """
        return {
            'proto_self': self.proto_self.to_dict(),
            'core_consciousness': self.core_consciousness.to_dict(),
            'extended_consciousness': self.extended_consciousness.to_dict(),
            'timestamp': datetime.now().isoformat(),
        }
