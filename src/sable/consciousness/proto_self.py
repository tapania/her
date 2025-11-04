"""
Proto-Self: The Foundation of Consciousness

Implements Damasio's proto-self - the most basic level of consciousness.
The proto-self is a collection of neural patterns that continuously represent
the body's state. It is non-conscious but essential for all conscious experience.

Key functions:
- Maintain body state representation
- Apply homeostatic regulation (return to equilibrium)
- Generate background emotions from body state
- Integrate emotional impacts into body state
"""

from datetime import datetime
from typing import Optional, Dict
from pathlib import Path

from sable.models.body_state import BodyState
from sable.database.queries import save_body_state, get_latest_body_state


class ProtoSelf:
    """
    Proto-self: Pre-conscious body state representation.

    The proto-self continuously maps the body's internal state across
    multiple dimensions (energy, stress, arousal, valence, etc.).

    This mapping is automatic and pre-conscious - you don't think about
    your heart rate, you just have it. But it provides the foundation
    for all emotional experience.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize proto-self.

        Args:
            db_path: Path to database (optional)
        """
        self.db_path = db_path
        self.current_state: Optional[BodyState] = None

    async def initialize(self) -> None:
        """
        Initialize proto-self by loading or creating body state.
        """
        # Try to load latest body state from database
        self.current_state = await get_latest_body_state(self.db_path)

        # If no state exists, create default state
        if self.current_state is None:
            self.current_state = BodyState()
            await self.save()

    async def get_state(self) -> BodyState:
        """
        Get current body state.

        Returns:
            Current BodyState
        """
        if self.current_state is None:
            await self.initialize()

        return self.current_state

    async def update_state(self, new_state: BodyState) -> None:
        """
        Update body state and save to database.

        Args:
            new_state: New BodyState
        """
        self.current_state = new_state
        await self.save()

    async def apply_decay(self, seconds_elapsed: Optional[float] = None) -> BodyState:
        """
        Apply homeostatic decay to body state.

        The body naturally regulates itself toward optimal states over time.
        This is the core of Damasio's homeostatic principle.

        Args:
            seconds_elapsed: How many seconds have passed (auto-calculated if None)

        Returns:
            New decayed BodyState
        """
        if self.current_state is None:
            await self.initialize()

        # Calculate time elapsed if not provided
        if seconds_elapsed is None:
            now = datetime.now()
            time_diff = now - self.current_state.timestamp
            seconds_elapsed = time_diff.total_seconds()

        # Apply decay
        new_state = self.current_state.apply_decay(seconds_elapsed)

        # Update and save
        await self.update_state(new_state)

        return new_state

    async def apply_body_changes(self, changes: Dict[str, float]) -> BodyState:
        """
        Apply changes to body state from emotions or external events.

        Args:
            changes: Dict of parameter -> change amount
                    Positive values increase, negative decrease
                    Example: {'energy': -0.2, 'stress': 0.3}

        Returns:
            Updated BodyState
        """
        if self.current_state is None:
            await self.initialize()

        # Create new state with changes applied
        state_dict = {
            'energy': self.current_state.energy,
            'stress': self.current_state.stress,
            'arousal': self.current_state.arousal,
            'valence': self.current_state.valence,
            'temperature': self.current_state.temperature,
            'tension': self.current_state.tension,
            'fatigue': self.current_state.fatigue,
            'pain': self.current_state.pain,
            'hunger': self.current_state.hunger,
            'heart_rate': self.current_state.heart_rate,
        }

        # Apply changes with clamping
        for param, change in changes.items():
            if param in state_dict:
                new_value = state_dict[param] + change
                # Clamp to valid ranges
                if param == 'valence':
                    state_dict[param] = max(-1.0, min(1.0, new_value))
                else:
                    state_dict[param] = max(0.0, min(1.0, new_value))

        # Create new BodyState (validation happens automatically)
        new_state = BodyState(**state_dict)

        # Update and save
        await self.update_state(new_state)

        return new_state

    def get_homeostatic_pressure(self) -> float:
        """
        Get current homeostatic pressure.

        High pressure indicates the body is far from optimal state.
        This pressure drives emotional responses and behavior.

        Returns:
            Pressure level (0-1)
        """
        if self.current_state is None:
            return 0.0

        return self.current_state.get_homeostatic_pressure()

    def get_background_emotion(self) -> str:
        """
        Get current background emotion based on body state.

        Background emotions (Damasio's term) are diffuse feelings arising
        from ongoing body state rather than specific objects/events.

        Examples: malaise, contentment, unease, vigor

        Returns:
            Background emotion name
        """
        if self.current_state is None:
            return "equanimity"

        return self.current_state.get_background_emotion()

    async def save(self) -> None:
        """Save current body state to database."""
        if self.current_state is not None:
            body_state_id = await save_body_state(self.current_state, self.db_path)
            self.current_state.id = body_state_id

    def to_dict(self) -> dict:
        """
        Export proto-self state as dictionary.

        Returns:
            Dict representation
        """
        if self.current_state is None:
            return {}

        return {
            'body_state': self.current_state.to_dict(),
            'homeostatic_pressure': self.get_homeostatic_pressure(),
            'background_emotion': self.get_background_emotion(),
        }
