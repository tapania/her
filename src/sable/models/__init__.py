"""
Data models for Sable's consciousness system.

These models represent the fundamental building blocks of Damasian consciousness:
- BodyState: Proto-self physiological parameters
- Emotion: Core consciousness emotional events
- Feeling: Conscious experience of emotions
- SomaticMarker: Learned associations between situations and emotions
- Memory: Autobiographical events with emotional salience
"""

from sable.models.body_state import BodyState
from sable.models.emotion import Emotion, EmotionType, Feeling
from sable.models.memory import Memory, SomaticMarker, Event

__all__ = [
    "BodyState",
    "Emotion",
    "EmotionType",
    "Feeling",
    "Memory",
    "SomaticMarker",
    "Event",
]
