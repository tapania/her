"""
Memory Models - Extended Consciousness Layer

Implements Damasio's concepts of:
- Somatic markers: Emotional tags for decision-making
- Autobiographical memory: Personal history with emotional salience
- Events: Raw experience log

Extended consciousness requires memory - the ability to place current
experience in the context of past and imagined future.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from sable.models.emotion import EmotionType


class Event(BaseModel):
    """
    Raw event: Something that happened.

    Events are the building blocks of experience. Not all events become
    memories - only those with sufficient emotional salience are encoded
    into autobiographical memory.

    Attributes:
        description: What happened
        context: Additional contextual information
        timestamp: When it happened
        emotional_impact: Immediate emotional response
    """

    description: str = Field(description="What happened")
    context: Optional[str] = Field(default=None, description="Additional context")
    timestamp: datetime = Field(default_factory=datetime.now)

    # Immediate emotional response to this event
    emotional_impact: dict[str, float] = Field(
        default_factory=dict,
        description="Immediate emotions: {emotion_type: intensity}"
    )

    # Metadata
    id: Optional[int] = None

    def get_emotional_salience(self) -> float:
        """
        Calculate overall emotional salience of this event.

        Salient events are more likely to become memories.
        Salience is higher for:
        - Intense emotions
        - Multiple simultaneous emotions
        - Negative emotions (negativity bias)
        """
        if not self.emotional_impact:
            return 0.1  # Low salience

        intensities = list(self.emotional_impact.values())
        max_intensity = max(intensities) if intensities else 0.0
        num_emotions = len(intensities)

        # Salience increases with intensity and number of emotions
        base_salience = max_intensity * (1 + 0.1 * num_emotions)

        return min(1.0, base_salience)

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "description": self.description,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "emotional_impact": str(self.emotional_impact),  # JSON string
        }


class Memory(BaseModel):
    """
    Autobiographical memory: Emotionally salient event that defines the self.

    Memories are not perfect recordings - they are reconstructed each time
    from fragments, colored by current emotional state.

    Damasio's key insight: Memory is fundamentally emotional. We remember
    what matters to us emotionally. Neutral events don't stick.

    Attributes:
        event: The original event
        emotional_salience: How emotionally significant (0-1)
        access_count: How many times this memory has been retrieved
        last_accessed: When it was last remembered
        narrative_role: How this memory fits into life story
        associated_emotions: Primary emotions linked to this memory
    """

    event: Event = Field(description="The event that became a memory")

    emotional_salience: float = Field(
        ge=0.0,
        le=1.0,
        description="How emotionally significant (determines retention)"
    )

    # Memory dynamics
    access_count: int = Field(default=0, description="Times retrieved")
    last_accessed: Optional[datetime] = None
    consolidation_level: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How well consolidated (1=deeply encoded)"
    )

    # Narrative integration
    narrative_role: Optional[str] = Field(
        default=None,
        description="Role in life story (e.g., 'turning point', 'formative experience')"
    )

    # Emotional associations
    associated_emotions: List[str] = Field(
        default_factory=list,
        description="Primary emotions linked to this memory"
    )

    # Identity relevance
    identity_relevance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How central to sense of self"
    )

    # Metadata
    id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)

    def access(self) -> "Memory":
        """
        Access this memory (simulate retrieval).

        Each retrieval:
        - Increases consolidation (memories strengthen with use)
        - Updates last_accessed timestamp
        - Increments access_count
        """
        new_memory = self.model_copy()
        new_memory.access_count += 1
        new_memory.last_accessed = datetime.now()

        # Consolidation increases with each access (up to limit)
        consolidation_gain = 0.05 * (1.0 - self.consolidation_level)
        new_memory.consolidation_level = min(
            1.0,
            self.consolidation_level + consolidation_gain
        )

        return new_memory

    def decay_over_time(self, days_elapsed: float) -> float:
        """
        Calculate memory decay over time.

        Memories fade without rehearsal, but:
        - High salience memories decay slower
        - Well-consolidated memories decay slower
        - Frequently accessed memories decay slower

        Returns:
            Decay factor (0-1), multiply by consolidation to get new strength
        """
        # Base decay rate (half-life in days)
        base_half_life = 30.0  # Memories fade over ~month without access

        # Factors that slow decay
        salience_factor = 1 + self.emotional_salience * 2  # High salience = slower decay
        consolidation_factor = 1 + self.consolidation_level  # Consolidated = slower decay
        access_factor = 1 + min(self.access_count * 0.1, 2.0)  # Accessed = slower decay

        effective_half_life = base_half_life * salience_factor * consolidation_factor * access_factor

        import math
        decay_constant = math.log(2) / effective_half_life
        decay_factor = math.exp(-decay_constant * days_elapsed)

        return decay_factor

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "event_id": self.event.id,
            "emotional_salience": self.emotional_salience,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "consolidation_level": self.consolidation_level,
            "narrative_role": self.narrative_role,
            "associated_emotions": ",".join(self.associated_emotions),
            "identity_relevance": self.identity_relevance,
            "created_at": self.created_at.isoformat(),
        }


class SomaticMarker(BaseModel):
    """
    Somatic marker: Learned emotional association for decision-making.

    Damasio's famous concept: When facing a decision, we don't just
    reason logically - we get "gut feelings" based on past emotional
    experiences. These are somatic markers.

    Process:
    1. Encounter a situation
    2. Body state changes (emotion) based on past experiences
    3. This feeling guides decision before conscious reasoning

    Example: Seeing a risky investment triggers subtle anxiety (learned
    from past losses), steering you away before you consciously analyze.

    Attributes:
        situation_pattern: Description of situation type
        emotion_type: What emotion is triggered
        valence: Positive (approach) or negative (avoid)
        strength: How strong the association (0-1)
        origin_memory_id: Which memory created this marker
    """

    situation_pattern: str = Field(
        description="Type of situation that triggers this marker"
    )

    emotion_type: EmotionType = Field(
        description="Emotion triggered by this situation"
    )

    valence: float = Field(
        ge=-1.0,
        le=1.0,
        description="Good/bad signal (-1=avoid, +1=approach)"
    )

    strength: float = Field(
        ge=0.0,
        le=1.0,
        description="Strength of association (confidence)"
    )

    # Learning history
    origin_memory_id: Optional[int] = Field(
        default=None,
        description="Memory that created this marker"
    )

    reinforcement_count: int = Field(
        default=1,
        description="How many times this association was reinforced"
    )

    last_activated: Optional[datetime] = None

    # Metadata
    id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)

    def activate(self, intensity_multiplier: float = 1.0) -> float:
        """
        Activate this somatic marker (trigger the gut feeling).

        Returns:
            Emotional intensity to inject (0-1)
        """
        self.last_activated = datetime.now()

        # Stronger markers produce stronger feelings
        return self.strength * intensity_multiplier

    def reinforce(self, outcome_valence: float) -> "SomaticMarker":
        """
        Reinforce or weaken this marker based on outcome.

        If outcome matches prediction (valence), strengthen.
        If outcome contradicts prediction, weaken.

        Args:
            outcome_valence: How good/bad the actual outcome was (-1 to +1)

        Returns:
            Updated marker
        """
        new_marker = self.model_copy()
        new_marker.reinforcement_count += 1

        # Agreement between prediction and outcome
        agreement = 1.0 - abs(self.valence - outcome_valence) / 2.0

        # Adjust strength based on agreement
        if agreement > 0.5:
            # Prediction was good, strengthen
            new_marker.strength = min(1.0, self.strength + 0.05)
        else:
            # Prediction was bad, weaken
            new_marker.strength = max(0.1, self.strength - 0.1)

        return new_marker

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "situation_pattern": self.situation_pattern,
            "emotion_type": self.emotion_type.value,
            "valence": self.valence,
            "strength": self.strength,
            "origin_memory_id": self.origin_memory_id,
            "reinforcement_count": self.reinforcement_count,
            "last_activated": self.last_activated.isoformat() if self.last_activated else None,
            "created_at": self.created_at.isoformat(),
        }
