"""
Core Consciousness: The Feeling of What Happens

Implements Damasio's core consciousness - the sense of "now" and "mine".

Core consciousness is the feeling that arises when:
1. An object (thought, perception, memory) modifies body state (emotion)
2. We become aware of that body state change (feeling)
3. We sense ourselves as the owner of this experience

This is Damasio's "feeling of what happens" - the core of being conscious.

Key components:
- Emotions: Body state changes triggered by stimuli
- Feelings: Conscious awareness of those body changes
- Somatic markers: Learned emotional associations for decision-making
"""

from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from sable.models.emotion import Emotion, EmotionType, Feeling
from sable.models.memory import SomaticMarker
from sable.models.body_state import BodyState
from sable.database.queries import (
    save_emotion,
    get_active_emotions,
    update_emotion,
    save_feeling,
    save_somatic_marker,
    get_somatic_markers,
    update_somatic_marker,
)


class CoreConsciousness:
    """
    Core consciousness: Emotions, feelings, and somatic markers.

    This layer transforms unconscious body states (proto-self) into
    conscious emotional experience.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize core consciousness.

        Args:
            db_path: Path to database (optional)
        """
        self.db_path = db_path
        self.active_emotions: List[Emotion] = []
        self.somatic_markers: List[SomaticMarker] = []

    async def initialize(self) -> None:
        """Load active emotions and somatic markers from database."""
        self.active_emotions = await get_active_emotions(self.db_path)
        self.somatic_markers = await get_somatic_markers(db_path=self.db_path)

    async def trigger_emotion(
        self,
        emotion_type: EmotionType,
        intensity: float,
        cause: str,
        body_state: Optional[BodyState] = None
    ) -> Emotion:
        """
        Trigger an emotion event.

        This is the moment when something (object, thought, memory) causes
        a body state change. The emotion happens automatically before
        conscious awareness.

        Args:
            emotion_type: Type of emotion
            intensity: Intensity 0-1
            cause: What triggered this emotion
            body_state: Current body state (used to generate body signature)

        Returns:
            The triggered Emotion
        """
        # Get default valence and arousal for this emotion type
        valence = Emotion.get_default_valence(emotion_type)
        arousal = Emotion.get_default_arousal(emotion_type)

        # Create emotion
        emotion = Emotion(
            type=emotion_type,
            intensity=intensity,
            valence=valence,
            arousal=arousal,
            cause=cause,
            timestamp=datetime.now(),
        )

        # Generate body signature
        emotion.body_signature = emotion.get_body_signature()

        # Save to database
        emotion_id = await save_emotion(emotion, self.db_path)
        emotion.id = emotion_id

        # Add to active emotions
        self.active_emotions.append(emotion)

        return emotion

    async def feel_emotion(
        self,
        emotion: Emotion,
        awareness_level: float = 0.8
    ) -> Feeling:
        """
        Create a feeling from an emotion.

        This is the crucial step where unconscious emotion becomes
        conscious feeling - Damasio's "feeling of what happens".

        The emotion (body state change) was automatic.
        The feeling (awareness of that change) requires consciousness.

        Args:
            emotion: The emotion to feel
            awareness_level: How consciously aware (0-1)

        Returns:
            The Feeling
        """
        feeling = Feeling(
            emotion=emotion,
            awareness_level=awareness_level,
            timestamp=datetime.now(),
        )

        # Generate verbal description
        feeling.description = feeling.verbalize()
        feeling.verbalized = True

        # Save to database
        feeling_id = await save_feeling(feeling, self.db_path)
        feeling.id = feeling_id

        return feeling

    async def apply_decay(self, seconds_elapsed: Optional[float] = None) -> List[Emotion]:
        """
        Apply decay to all active emotions.

        Emotions fade over time as the body returns to homeostasis.

        Args:
            seconds_elapsed: Seconds elapsed (auto-calculated if None)

        Returns:
            List of updated emotions
        """
        if not self.active_emotions:
            return []

        updated_emotions = []

        for emotion in self.active_emotions:
            # Calculate time elapsed if not provided
            if seconds_elapsed is None:
                now = datetime.now()
                time_diff = now - emotion.timestamp
                time_elapsed = time_diff.total_seconds()
            else:
                time_elapsed = seconds_elapsed

            # Apply decay
            decayed_emotion = emotion.apply_decay(time_elapsed)

            # Update in database
            await update_emotion(decayed_emotion, self.db_path)

            updated_emotions.append(decayed_emotion)

        # Remove fully decayed emotions from active list
        self.active_emotions = [e for e in updated_emotions if not e.decayed]

        return updated_emotions

    async def get_somatic_marker_for_situation(
        self,
        situation_description: str,
        min_strength: float = 0.3
    ) -> Optional[SomaticMarker]:
        """
        Get somatic marker (gut feeling) for a situation.

        This is how emotions guide decision-making: You encounter a
        situation, and before conscious reasoning, a subtle emotional
        response (somatic marker) biases you toward or away from options.

        Args:
            situation_description: Description of current situation
            min_strength: Minimum marker strength to return

        Returns:
            Strongest matching SomaticMarker, or None
        """
        # Get markers matching this situation
        markers = await get_somatic_markers(
            situation_pattern=situation_description,
            min_strength=min_strength,
            db_path=self.db_path
        )

        if not markers:
            return None

        # Return strongest marker
        return markers[0]

    async def create_somatic_marker(
        self,
        situation_pattern: str,
        emotion_type: EmotionType,
        valence: float,
        strength: float,
        origin_memory_id: Optional[int] = None
    ) -> SomaticMarker:
        """
        Create a new somatic marker from experience.

        When an emotional experience teaches you something about a type
        of situation, a somatic marker is formed.

        Args:
            situation_pattern: Type of situation
            emotion_type: What emotion to trigger
            valence: Good/bad signal (-1 to +1)
            strength: Association strength (0-1)
            origin_memory_id: Memory that created this marker

        Returns:
            The created SomaticMarker
        """
        marker = SomaticMarker(
            situation_pattern=situation_pattern,
            emotion_type=emotion_type,
            valence=valence,
            strength=strength,
            origin_memory_id=origin_memory_id,
            created_at=datetime.now(),
        )

        # Save to database
        marker_id = await save_somatic_marker(marker, self.db_path)
        marker.id = marker_id

        # Add to cached markers
        self.somatic_markers.append(marker)

        return marker

    async def reinforce_somatic_marker(
        self,
        marker: SomaticMarker,
        outcome_valence: float
    ) -> SomaticMarker:
        """
        Reinforce or weaken a somatic marker based on outcome.

        Somatic markers are learned: they strengthen when predictions
        are correct, weaken when wrong.

        Args:
            marker: The marker to update
            outcome_valence: How good/bad the actual outcome was

        Returns:
            Updated marker
        """
        updated_marker = marker.reinforce(outcome_valence)

        # Update in database
        await update_somatic_marker(updated_marker, self.db_path)

        # Update in cache
        for i, m in enumerate(self.somatic_markers):
            if m.id == updated_marker.id:
                self.somatic_markers[i] = updated_marker
                break

        return updated_marker

    def get_current_emotional_state(self) -> Dict[str, float]:
        """
        Get aggregated current emotional state.

        Returns dict of emotion type -> total intensity.
        Multiple emotions can coexist.

        Returns:
            Dict of emotion_type -> intensity
        """
        emotion_totals: Dict[str, float] = {}

        for emotion in self.active_emotions:
            if not emotion.decayed:
                emotion_type = emotion.type.value
                current_intensity = emotion_totals.get(emotion_type, 0.0)
                emotion_totals[emotion_type] = current_intensity + emotion.intensity

        # Cap at 1.0
        return {k: min(1.0, v) for k, v in emotion_totals.items()}

    def get_overall_valence_arousal(self) -> tuple[float, float]:
        """
        Get overall emotional valence and arousal.

        Returns:
            Tuple of (valence, arousal) averaging all active emotions
        """
        if not self.active_emotions:
            return (0.0, 0.5)  # Neutral

        active = [e for e in self.active_emotions if not e.decayed]
        if not active:
            return (0.0, 0.5)

        total_valence = sum(e.valence * e.intensity for e in active)
        total_arousal = sum(e.arousal * e.intensity for e in active)
        total_intensity = sum(e.intensity for e in active)

        if total_intensity == 0:
            return (0.0, 0.5)

        avg_valence = total_valence / total_intensity
        avg_arousal = total_arousal / total_intensity

        return (avg_valence, avg_arousal)

    def to_dict(self) -> dict:
        """
        Export core consciousness state as dictionary.

        Returns:
            Dict representation
        """
        valence, arousal = self.get_overall_valence_arousal()

        return {
            'active_emotions': [
                {
                    'type': e.type.value,
                    'intensity': e.intensity,
                    'cause': e.cause,
                }
                for e in self.active_emotions if not e.decayed
            ],
            'emotional_state': self.get_current_emotional_state(),
            'overall_valence': valence,
            'overall_arousal': arousal,
            'num_somatic_markers': len(self.somatic_markers),
        }
