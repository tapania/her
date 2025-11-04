"""
Body State Model - Proto-Self Layer

Represents Damasio's proto-self: the most basic level of consciousness
consisting of body state representation and homeostatic regulation.

The proto-self is non-conscious but provides the foundation for all
conscious experience by mapping the body's internal landscape.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class BodyState(BaseModel):
    """
    Represents the body's internal state at a moment in time.

    This implements Damasio's concept of the proto-self - a collection of
    neural patterns that map the body's state across multiple dimensions.

    Key Damasian principles:
    - Homeostatic regulation: The body seeks equilibrium
    - Interoception: Internal body signals (vs. exteroception)
    - Background emotions: Ongoing body state independent of objects

    Attributes:
        timestamp: When this state was recorded
        energy: Available energy level (0=exhausted, 1=maximum energy)
        stress: Current stress/tension level (0=relaxed, 1=extreme stress)
        arousal: Activation level (0=calm/sleepy, 1=highly aroused/alert)
        valence: Emotional positivity/negativity (-1=very negative, +1=very positive)
        temperature: Body temperature perception (0=cold, 1=hot)
        tension: Muscular tension (0=relaxed, 1=very tense)
        fatigue: Accumulated fatigue (0=fresh, 1=exhausted)
        pain: Pain level (0=none, 1=severe)
        hunger: Hunger/satiation (0=satiated, 1=very hungry)
        heart_rate: Normalized heart rate (0=resting, 1=maximum)
    """

    timestamp: datetime = Field(default_factory=datetime.now)

    # Core homeostatic variables
    energy: float = Field(default=0.7, ge=0.0, le=1.0, description="Energy level")
    stress: float = Field(default=0.3, ge=0.0, le=1.0, description="Stress level")
    arousal: float = Field(default=0.5, ge=0.0, le=1.0, description="Arousal/activation")
    valence: float = Field(default=0.1, ge=-1.0, le=1.0, description="Positive/negative")

    # Secondary body parameters
    temperature: float = Field(default=0.5, ge=0.0, le=1.0, description="Temperature perception")
    tension: float = Field(default=0.3, ge=0.0, le=1.0, description="Muscular tension")
    fatigue: float = Field(default=0.2, ge=0.0, le=1.0, description="Fatigue level")
    pain: float = Field(default=0.0, ge=0.0, le=1.0, description="Pain level")
    hunger: float = Field(default=0.3, ge=0.0, le=1.0, description="Hunger level")
    heart_rate: float = Field(default=0.5, ge=0.0, le=1.0, description="Heart rate (normalized)")

    # Metadata
    id: Optional[int] = None

    @field_validator('energy', 'stress', 'arousal', 'temperature', 'tension',
                     'fatigue', 'pain', 'hunger', 'heart_rate')
    @classmethod
    def validate_unit_interval(cls, v: float) -> float:
        """Ensure values stay within [0, 1]."""
        return max(0.0, min(1.0, v))

    @field_validator('valence')
    @classmethod
    def validate_valence(cls, v: float) -> float:
        """Ensure valence stays within [-1, 1]."""
        return max(-1.0, min(1.0, v))

    def get_homeostatic_pressure(self) -> float:
        """
        Calculate overall homeostatic pressure (drive to restore balance).

        High pressure indicates the body is far from optimal state and
        needs regulation. This drives emotional responses and behavior.

        Returns:
            Float 0-1 indicating deviation from homeostatic baselines
        """
        # Define ideal baselines
        ideal_energy = 0.7
        ideal_stress = 0.2
        ideal_arousal = 0.5
        ideal_valence = 0.2
        ideal_tension = 0.2
        ideal_fatigue = 0.1

        # Calculate deviations
        deviations = [
            abs(self.energy - ideal_energy) * 1.2,  # Energy very important
            abs(self.stress - ideal_stress) * 1.0,
            abs(self.arousal - ideal_arousal) * 0.8,
            abs(self.valence - ideal_valence) * 1.0,
            abs(self.tension - ideal_tension) * 0.7,
            abs(self.fatigue - ideal_fatigue) * 1.0,
            self.pain * 1.5,  # Pain always bad
            abs(self.hunger - 0.3) * 0.6,  # Slight hunger is normal
        ]

        # Average weighted deviation
        return sum(deviations) / len(deviations)

    def get_background_emotion(self) -> str:
        """
        Determine the background emotion based on body state.

        Background emotions (Damasio's term) are diffuse feelings
        arising from ongoing body state rather than specific objects/events.

        Returns:
            String describing the background emotional tone
        """
        if self.energy > 0.7 and self.valence > 0.3 and self.stress < 0.3:
            return "vigor"
        elif self.energy < 0.3 and self.fatigue > 0.6:
            return "malaise"
        elif self.stress > 0.7 and self.tension > 0.6:
            return "unease"
        elif self.arousal < 0.3 and self.energy < 0.5:
            return "discouragement"
        elif self.valence > 0.4 and self.stress < 0.4:
            return "contentment"
        elif self.arousal > 0.7 and self.valence > 0:
            return "enthusiasm"
        elif self.arousal > 0.7 and self.valence < 0:
            return "tension"
        else:
            return "equanimity"

    def apply_decay(self, seconds_elapsed: float) -> "BodyState":
        """
        Apply homeostatic decay toward baseline values over time.

        The body naturally regulates itself toward optimal states.
        This implements Damasio's homeostatic principle - the fundamental
        drive of living systems to maintain internal balance.

        Args:
            seconds_elapsed: Time since last state update

        Returns:
            New BodyState with decayed values
        """
        # Decay rates (half-life in seconds)
        energy_hl = 3600  # Energy decays slowly (1 hour)
        stress_hl = 1800  # Stress decays faster (30 min)
        arousal_hl = 600   # Arousal decays quickly (10 min)
        valence_hl = 1200  # Valence decays moderately (20 min)
        tension_hl = 1800
        fatigue_hl = 7200  # Fatigue accumulates/decays very slowly
        pain_hl = 3600

        # Baselines (where values decay toward)
        from sable.decay.decay_functions import exponential_decay_to_baseline

        new_state = self.model_copy()
        new_state.timestamp = datetime.now()

        new_state.energy = exponential_decay_to_baseline(
            self.energy, 0.7, energy_hl, seconds_elapsed
        )
        new_state.stress = exponential_decay_to_baseline(
            self.stress, 0.2, stress_hl, seconds_elapsed
        )
        new_state.arousal = exponential_decay_to_baseline(
            self.arousal, 0.5, arousal_hl, seconds_elapsed
        )
        new_state.valence = exponential_decay_to_baseline(
            self.valence, 0.1, valence_hl, seconds_elapsed
        )
        new_state.tension = exponential_decay_to_baseline(
            self.tension, 0.2, tension_hl, seconds_elapsed
        )
        new_state.fatigue = exponential_decay_to_baseline(
            self.fatigue, 0.1, fatigue_hl, seconds_elapsed
        )
        new_state.pain = exponential_decay_to_baseline(
            self.pain, 0.0, pain_hl, seconds_elapsed
        )

        # Hunger increases over time (inverted decay)
        hunger_growth_rate = 0.1 / 3600  # Grows slowly
        new_state.hunger = min(1.0, self.hunger + hunger_growth_rate * seconds_elapsed)

        return new_state

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "energy": self.energy,
            "stress": self.stress,
            "arousal": self.arousal,
            "valence": self.valence,
            "temperature": self.temperature,
            "tension": self.tension,
            "fatigue": self.fatigue,
            "pain": self.pain,
            "hunger": self.hunger,
            "heart_rate": self.heart_rate,
        }
