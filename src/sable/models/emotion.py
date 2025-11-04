"""
Emotion Models - Core Consciousness Layer

Implements Damasio's distinction between emotions (body states) and
feelings (conscious experience of emotions).

Key Damasian concepts:
- Emotions are automated body-state changes in response to stimuli
- Feelings are the conscious perception of those body changes
- Somatic markers link emotions to decision-making
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EmotionType(str, Enum):
    """
    Primary and background emotion types per Damasio's taxonomy.

    Primary Emotions (Universal, Fast, Survival-related):
    - fear, anger, sadness, joy, disgust, surprise

    Background Emotions (Diffuse, Ongoing, Body-state related):
    - contentment, malaise, unease, tension, enthusiasm, discouragement

    Social Emotions (Complex, Learned):
    - shame, guilt, pride, admiration, contempt, compassion
    """

    # Primary emotions (Damasio's "basic emotions")
    FEAR = "fear"
    ANGER = "anger"
    SADNESS = "sadness"
    JOY = "joy"
    DISGUST = "disgust"
    SURPRISE = "surprise"

    # Background emotions
    CONTENTMENT = "contentment"
    MALAISE = "malaise"
    UNEASE = "unease"
    TENSION = "tension"
    ENTHUSIASM = "enthusiasm"
    DISCOURAGEMENT = "discouragement"

    # Social emotions
    SHAME = "shame"
    GUILT = "guilt"
    PRIDE = "pride"
    ADMIRATION = "admiration"
    CONTEMPT = "contempt"
    COMPASSION = "compassion"

    # Complex blended states
    DESIRE = "desire"
    CURIOSITY = "curiosity"
    ANTICIPATION = "anticipation"
    FRUSTRATION = "frustration"


class Emotion(BaseModel):
    """
    An emotion event: automated body-state change in response to a stimulus.

    Emotions are pre-conscious. They are patterns of chemical and neural
    responses that change the body state. We become conscious of them
    through feelings.

    Attributes:
        type: Category of emotion
        intensity: Strength (0=barely present, 1=overwhelming)
        valence: Positive/negative quality (-1 to +1)
        arousal: Activation level (0=calm, 1=highly activated)
        timestamp: When this emotion was triggered
        cause: What triggered this emotion (object, event, thought)
        body_signature: Specific body changes (heart rate, tension, etc.)
    """

    type: EmotionType = Field(description="Type of emotion")
    intensity: float = Field(ge=0.0, le=1.0, description="Intensity 0-1")
    valence: float = Field(ge=-1.0, le=1.0, description="Positive/negative quality")
    arousal: float = Field(ge=0.0, le=1.0, description="Activation level")

    timestamp: datetime = Field(default_factory=datetime.now)
    cause: str = Field(description="What triggered this emotion")

    # Body changes associated with this emotion
    body_signature: dict[str, float] = Field(
        default_factory=dict,
        description="Body parameter changes (heart_rate, tension, temperature, etc.)"
    )

    # Metadata
    id: Optional[int] = None
    decayed: bool = Field(default=False, description="Has this emotion fully decayed?")

    @staticmethod
    def get_default_valence(emotion_type: EmotionType) -> float:
        """Get typical valence for this emotion type."""
        valence_map = {
            EmotionType.JOY: 0.8,
            EmotionType.CONTENTMENT: 0.6,
            EmotionType.ENTHUSIASM: 0.7,
            EmotionType.PRIDE: 0.6,
            EmotionType.ADMIRATION: 0.5,
            EmotionType.COMPASSION: 0.3,
            EmotionType.SURPRISE: 0.0,  # Neutral (can be positive or negative)
            EmotionType.CURIOSITY: 0.2,
            EmotionType.ANTICIPATION: 0.3,
            EmotionType.FEAR: -0.7,
            EmotionType.ANGER: -0.6,
            EmotionType.SADNESS: -0.7,
            EmotionType.DISGUST: -0.6,
            EmotionType.SHAME: -0.8,
            EmotionType.GUILT: -0.7,
            EmotionType.CONTEMPT: -0.4,
            EmotionType.MALAISE: -0.5,
            EmotionType.UNEASE: -0.4,
            EmotionType.TENSION: -0.3,
            EmotionType.DISCOURAGEMENT: -0.6,
            EmotionType.FRUSTRATION: -0.5,
            EmotionType.DESIRE: 0.4,
        }
        return valence_map.get(emotion_type, 0.0)

    @staticmethod
    def get_default_arousal(emotion_type: EmotionType) -> float:
        """Get typical arousal for this emotion type."""
        arousal_map = {
            # High arousal
            EmotionType.FEAR: 0.9,
            EmotionType.ANGER: 0.85,
            EmotionType.SURPRISE: 0.9,
            EmotionType.ENTHUSIASM: 0.8,
            EmotionType.ANTICIPATION: 0.7,
            EmotionType.FRUSTRATION: 0.75,

            # Medium arousal
            EmotionType.JOY: 0.6,
            EmotionType.DESIRE: 0.65,
            EmotionType.CURIOSITY: 0.6,
            EmotionType.TENSION: 0.7,
            EmotionType.UNEASE: 0.6,
            EmotionType.PRIDE: 0.5,

            # Low arousal
            EmotionType.SADNESS: 0.3,
            EmotionType.CONTENTMENT: 0.3,
            EmotionType.MALAISE: 0.3,
            EmotionType.DISCOURAGEMENT: 0.35,
            EmotionType.COMPASSION: 0.4,
            EmotionType.ADMIRATION: 0.4,

            # Very low arousal
            EmotionType.DISGUST: 0.5,
            EmotionType.CONTEMPT: 0.4,
            EmotionType.SHAME: 0.4,
            EmotionType.GUILT: 0.45,
        }
        return arousal_map.get(emotion_type, 0.5)

    def get_body_signature(self) -> dict[str, float]:
        """
        Generate typical body changes for this emotion type.

        Each emotion has a characteristic "body signature" - a pattern
        of changes across multiple physiological dimensions.
        """
        base_signatures = {
            EmotionType.FEAR: {
                'heart_rate': 0.9,
                'tension': 0.8,
                'temperature': 0.3,  # Cold
                'energy': -0.2,
                'stress': 0.8,
            },
            EmotionType.ANGER: {
                'heart_rate': 0.85,
                'tension': 0.9,
                'temperature': 0.8,  # Hot
                'energy': 0.3,
                'stress': 0.7,
            },
            EmotionType.JOY: {
                'heart_rate': 0.7,
                'tension': -0.2,  # Relaxed
                'energy': 0.4,
                'stress': -0.3,
            },
            EmotionType.SADNESS: {
                'heart_rate': 0.3,
                'tension': 0.4,
                'energy': -0.4,
                'fatigue': 0.5,
            },
            EmotionType.CONTENTMENT: {
                'tension': -0.3,
                'stress': -0.4,
                'energy': 0.2,
            },
        }

        signature = base_signatures.get(self.type, {})

        # Scale by intensity
        return {key: val * self.intensity for key, val in signature.items()}

    def apply_decay(self, seconds_elapsed: float) -> "Emotion":
        """
        Apply decay to emotion intensity over time.

        Returns a new Emotion with decayed intensity.
        """
        from sable.decay.decay_functions import (
            valence_asymmetric_decay,
            decay_config_for_emotion,
        )

        config = decay_config_for_emotion(self.type.value)

        new_intensity = valence_asymmetric_decay(
            current_intensity=self.intensity,
            valence=self.valence,
            base_half_life=config['half_life'],
            time_elapsed=seconds_elapsed,
            baseline=config['baseline'],
        )

        new_emotion = self.model_copy()
        new_emotion.intensity = new_intensity
        new_emotion.timestamp = datetime.now()

        # Mark as decayed if intensity drops below threshold
        if new_intensity < 0.05:
            new_emotion.decayed = True

        return new_emotion

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "type": self.type.value,
            "intensity": self.intensity,
            "valence": self.valence,
            "arousal": self.arousal,
            "timestamp": self.timestamp.isoformat(),
            "cause": self.cause,
            "body_signature": str(self.body_signature),  # JSON string
            "decayed": self.decayed,
        }


class Feeling(BaseModel):
    """
    A feeling: The conscious experience of an emotion.

    Damasio's key insight: Emotions and feelings are different!
    - Emotion: Body state change (can be unconscious)
    - Feeling: Awareness of that body state change

    Feelings require core consciousness - the integration of:
    1. Current body state (emotion)
    2. The object that caused it
    3. The sense of "now" and "mine"

    This is Damasio's "feeling of what happens" - the core of consciousness.

    Attributes:
        emotion: The underlying emotion being felt
        awareness_level: How consciously aware (0=barely noticed, 1=fully aware)
        verbalized: Has this feeling been put into words?
        description: Optional verbal description of the feeling
    """

    emotion: Emotion = Field(description="The emotion being felt")
    awareness_level: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="How consciously aware of this feeling"
    )
    verbalized: bool = Field(default=False, description="Has been put into words?")
    description: Optional[str] = Field(default=None, description="Verbal description")

    timestamp: datetime = Field(default_factory=datetime.now)
    id: Optional[int] = None

    def verbalize(self) -> str:
        """
        Generate a verbal description of this feeling.

        This simulates the process of putting feelings into words - a key
        aspect of extended consciousness and emotional regulation.
        """
        intensity_words = {
            (0.0, 0.2): "slightly",
            (0.2, 0.4): "somewhat",
            (0.4, 0.6): "moderately",
            (0.6, 0.8): "quite",
            (0.8, 1.0): "extremely",
        }

        intensity_desc = next(
            desc for (low, high), desc in intensity_words.items()
            if low <= self.emotion.intensity < high
        )

        emotion_name = self.emotion.type.value

        if self.emotion.cause:
            return f"I feel {intensity_desc} {emotion_name} about {self.emotion.cause}"
        else:
            return f"I feel {intensity_desc} {emotion_name}"

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "emotion_id": self.emotion.id,
            "awareness_level": self.awareness_level,
            "verbalized": self.verbalized,
            "description": self.description or self.verbalize(),
            "timestamp": self.timestamp.isoformat(),
        }
