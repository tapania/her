"""
Decay and Homeostasis System

Implements time-based emotional and physiological decay functions based on
Damasio's principle of homeostatic regulation: living systems naturally
return to equilibrium states over time.

Key principles:
- Exponential decay: Most emotional/body states decay exponentially
- Homeostatic baselines: Each parameter has an optimal resting value
- Valence asymmetry: Negative experiences persist longer than positive
- Arousal coupling: High arousal slows decay initially
"""

from sable.decay.decay_functions import (
    exponential_decay,
    exponential_decay_to_baseline,
    valence_asymmetric_decay,
    arousal_coupled_decay,
)

__all__ = [
    "exponential_decay",
    "exponential_decay_to_baseline",
    "valence_asymmetric_decay",
    "arousal_coupled_decay",
]
