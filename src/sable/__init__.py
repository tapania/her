"""
Sable: Damasian Consciousness Framework

A complete implementation of Antonio Damasio's three-level consciousness model:
- Proto-self: Body state representation and homeostatic regulation
- Core consciousness: Emotions, feelings, and somatic markers
- Extended consciousness: Autobiographical memory and narrative self

This system provides authentic emotional dynamics with:
- Time-based decay toward homeostatic baselines
- Conversation-driven emotional responses
- Body state simulation
- Learned somatic markers for decision-making
"""

__version__ = "0.1.0"
__author__ = "Taala"

from sable.state.state_manager import StateManager

__all__ = ["StateManager"]
