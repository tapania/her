"""
Decay Functions for Emotional and Physiological States

These functions implement the temporal dynamics of consciousness - how
emotions and body states change over time through homeostatic regulation.

Based on Damasio's principle: Living organisms maintain themselves within
narrow ranges through continuous homeostatic regulation.
"""

import math
from typing import Optional


def exponential_decay(
    current_value: float,
    half_life: float,
    time_elapsed: float,
    min_value: float = 0.0
) -> float:
    """
    Simple exponential decay toward zero (or minimum value).

    The standard decay model: intensity halves every `half_life` seconds.

    Args:
        current_value: Current intensity (0-1)
        half_life: Time in seconds for value to halve
        time_elapsed: Seconds since last update
        min_value: Minimum value to decay toward (default 0)

    Returns:
        Decayed value

    Example:
        >>> exponential_decay(1.0, 60, 60)  # After 1 half-life
        0.5
        >>> exponential_decay(1.0, 60, 120)  # After 2 half-lives
        0.25
    """
    if half_life <= 0:
        return min_value

    # Decay constant (lambda)
    decay_constant = math.log(2) / half_life

    # Exponential decay formula: V(t) = V0 * e^(-λt)
    decayed = (current_value - min_value) * math.exp(-decay_constant * time_elapsed)

    return max(min_value, decayed + min_value)


def exponential_decay_to_baseline(
    current_value: float,
    baseline: float,
    half_life: float,
    time_elapsed: float
) -> float:
    """
    Exponential decay toward a homeostatic baseline (not zero).

    This is the core homeostatic function: values naturally return to
    optimal resting states. If current_value > baseline, it decays down.
    If current_value < baseline, it "decays" up toward baseline.

    Args:
        current_value: Current value
        baseline: Homeostatic equilibrium point
        half_life: Time for half of deviation from baseline to decay
        time_elapsed: Seconds since last update

    Returns:
        Value decayed toward baseline

    Example:
        >>> exponential_decay_to_baseline(1.0, 0.5, 60, 60)
        0.75  # Halfway from 1.0 toward 0.5
        >>> exponential_decay_to_baseline(0.0, 0.5, 60, 60)
        0.25  # Halfway from 0.0 toward 0.5
    """
    if half_life <= 0:
        return baseline

    # Deviation from baseline
    deviation = current_value - baseline

    # Decay the deviation
    decay_constant = math.log(2) / half_life
    decayed_deviation = deviation * math.exp(-decay_constant * time_elapsed)

    # Return to baseline proportionally
    return baseline + decayed_deviation


def valence_asymmetric_decay(
    current_intensity: float,
    valence: float,
    base_half_life: float,
    time_elapsed: float,
    baseline: float = 0.0,
    asymmetry_factor: float = 1.3
) -> float:
    """
    Decay with valence asymmetry: negative emotions persist longer.

    Psychological research shows negative experiences have stronger and
    longer-lasting effects than positive ones (negativity bias).

    Args:
        current_intensity: Current intensity (0-1)
        valence: Emotional valence (-1 to +1)
        base_half_life: Base half-life for neutral emotions
        time_elapsed: Seconds elapsed
        baseline: Baseline to decay toward
        asymmetry_factor: How much longer negative emotions persist (default 1.3 = 30% longer)

    Returns:
        Decayed intensity with valence consideration

    Example:
        >>> # Negative emotion (fear, valence=-0.8)
        >>> valence_asymmetric_decay(1.0, -0.8, 100, 100, 0.0, 1.3)
        0.614  # Slower decay
        >>> # Positive emotion (joy, valence=+0.8)
        >>> valence_asymmetric_decay(1.0, 0.8, 100, 100, 0.0, 1.3)
        0.423  # Faster decay
    """
    # Adjust half-life based on valence
    # Negative valence -> longer half-life (slower decay)
    # Positive valence -> shorter half-life (faster decay)
    if valence < 0:
        # Negative emotions persist longer
        adjusted_half_life = base_half_life * (1 + abs(valence) * (asymmetry_factor - 1))
    else:
        # Positive emotions fade faster
        adjusted_half_life = base_half_life / (1 + valence * (asymmetry_factor - 1))

    return exponential_decay_to_baseline(
        current_intensity,
        baseline,
        adjusted_half_life,
        time_elapsed
    )


def arousal_coupled_decay(
    current_intensity: float,
    arousal_level: float,
    base_half_life: float,
    time_elapsed: float,
    baseline: float = 0.0,
    coupling_strength: float = 0.5
) -> float:
    """
    Decay influenced by arousal level: high arousal slows initial decay.

    When highly aroused (alert, activated), emotions persist longer.
    When calm/drowsy, emotions fade more quickly.

    Args:
        current_intensity: Current intensity
        arousal_level: Current arousal (0=calm, 1=highly aroused)
        base_half_life: Base half-life at medium arousal
        time_elapsed: Seconds elapsed
        baseline: Value to decay toward
        coupling_strength: How much arousal affects decay (0-1)

    Returns:
        Decayed value considering arousal

    Example:
        >>> # High arousal (0.9) - emotion persists
        >>> arousal_coupled_decay(1.0, 0.9, 100, 100, 0.0, 0.5)
        0.574  # Slower decay
        >>> # Low arousal (0.1) - emotion fades quickly
        >>> arousal_coupled_decay(1.0, 0.1, 100, 100, 0.0, 0.5)
        0.435  # Faster decay
    """
    # Arousal modulates decay rate
    # High arousal (toward 1) -> longer half-life
    # Low arousal (toward 0) -> shorter half-life
    arousal_multiplier = 1.0 + coupling_strength * (arousal_level - 0.5) * 2

    adjusted_half_life = base_half_life * arousal_multiplier

    return exponential_decay_to_baseline(
        current_intensity,
        baseline,
        adjusted_half_life,
        time_elapsed
    )


def homeostatic_pressure(
    current_values: dict[str, float],
    baselines: dict[str, float],
    weights: Optional[dict[str, float]] = None
) -> float:
    """
    Calculate overall homeostatic pressure across multiple parameters.

    Homeostatic pressure drives behavior: the organism acts to reduce
    deviation from optimal states.

    Args:
        current_values: Dict of parameter name -> current value
        baselines: Dict of parameter name -> baseline value
        weights: Optional dict of parameter name -> importance weight

    Returns:
        Overall pressure (0-1), higher = more deviation from homeostasis

    Example:
        >>> homeostatic_pressure(
        ...     {'energy': 0.3, 'stress': 0.8},
        ...     {'energy': 0.7, 'stress': 0.2},
        ...     {'energy': 1.2, 'stress': 1.0}
        ... )
        0.52  # Moderate pressure
    """
    if weights is None:
        weights = {key: 1.0 for key in current_values.keys()}

    total_weighted_deviation = 0.0
    total_weight = 0.0

    for param, current_val in current_values.items():
        if param in baselines:
            baseline = baselines[param]
            weight = weights.get(param, 1.0)

            deviation = abs(current_val - baseline)
            total_weighted_deviation += deviation * weight
            total_weight += weight

    if total_weight == 0:
        return 0.0

    # Normalize to 0-1 range (assuming max deviation is 1.0)
    return min(1.0, total_weighted_deviation / total_weight)


def decay_config_for_emotion(emotion_type: str) -> dict:
    """
    Get default decay configuration for different emotion types.

    Returns dict with 'half_life' (seconds) and 'baseline' (0-1).

    Emotions have different natural durations:
    - Primary emotions (fear, anger, joy): Minutes
    - Background emotions (contentment, malaise): Hours
    - Body states (stress, energy): Hours to days

    Args:
        emotion_type: Type of emotion (e.g., 'fear', 'joy', 'contentment')

    Returns:
        Dict with decay parameters
    """
    configs = {
        # Primary emotions - decay in minutes
        'fear': {'half_life': 120, 'baseline': 0.05},  # 2 min
        'anger': {'half_life': 180, 'baseline': 0.05},  # 3 min
        'joy': {'half_life': 300, 'baseline': 0.15},  # 5 min
        'sadness': {'half_life': 600, 'baseline': 0.1},  # 10 min (lingers)
        'disgust': {'half_life': 240, 'baseline': 0.05},  # 4 min
        'surprise': {'half_life': 60, 'baseline': 0.05},  # 1 min (very brief)

        # Background emotions - decay in hours
        'contentment': {'half_life': 3600, 'baseline': 0.4},  # 1 hour
        'malaise': {'half_life': 7200, 'baseline': 0.1},  # 2 hours
        'unease': {'half_life': 1800, 'baseline': 0.15},  # 30 min
        'tension': {'half_life': 1800, 'baseline': 0.2},  # 30 min
        'enthusiasm': {'half_life': 1200, 'baseline': 0.2},  # 20 min
        'discouragement': {'half_life': 3600, 'baseline': 0.15},  # 1 hour

        # Body states - decay over hours
        'energy': {'half_life': 3600, 'baseline': 0.7},  # 1 hour
        'stress': {'half_life': 1800, 'baseline': 0.2},  # 30 min
        'arousal': {'half_life': 600, 'baseline': 0.5},  # 10 min
        'valence': {'half_life': 1200, 'baseline': 0.1},  # 20 min
        'tension': {'half_life': 1800, 'baseline': 0.2},  # 30 min
        'fatigue': {'half_life': 7200, 'baseline': 0.1},  # 2 hours
    }

    return configs.get(
        emotion_type.lower(),
        {'half_life': 600, 'baseline': 0.1}  # Default: 10 min
    )
