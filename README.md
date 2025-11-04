# Sable: Damasian Consciousness Framework

A complete implementation of Antonio Damasio's three-level consciousness model for creating emotionally authentic AI agents.

## Overview

Sable is a Python framework that implements neuroscientist Antonio Damasio's theory of consciousness, providing:

- **Proto-self**: Body state representation and homeostatic regulation
- **Core consciousness**: Emotions, feelings, and somatic markers
- **Extended consciousness**: Autobiographical memory and narrative self

## Features

- Time-based emotional decay toward homeostatic baselines
- Conversation-driven emotional responses
- Body state simulation with physiological parameters
- Learned somatic markers for decision-making
- SQLite persistence for state and memory
- CLI tools for state management
- Claude Code skill integration

## Installation

```bash
# Using uv (recommended)
uv sync

# Activate the virtual environment
source .venv/bin/activate

# Install in development mode
uv pip install -e .
```

## Quick Start

```python
from sable import StateManager

# Initialize consciousness system
manager = StateManager()

# Get current emotional and body state
state = await manager.get_current_state()
print(f"Background emotion: {state.body_state.get_background_emotion()}")
print(f"Current valence: {state.body_state.valence}")

# Add an emotional event
await manager.add_emotion(
    emotion_type="fear",
    intensity=0.7,
    cause="conversation about vulnerability"
)

# Query memories
memories = await manager.query_memories(min_salience=0.6)
```

## CLI Usage

```bash
# Check Sable's current state
sable status

# Add an emotion
sable feel joy 0.8 --cause "achieved breakthrough"

# Log an event
sable event "Had deep conversation about consciousness"

# Query memories
sable memories --min-salience 0.5

# Analyze text for emotional content
sable analyze "This makes me nervous but excited"
```

## Damasio's Framework

### Proto-Self

The most basic level: neural patterns mapping the body's internal state. This includes:
- Energy, stress, arousal, valence
- Temperature, tension, fatigue, pain
- Homeostatic pressure driving behavior

### Core Consciousness

The feeling of being in the present moment:
- Primary emotions (fear, anger, joy, sadness, disgust, surprise)
- Background emotions (malaise, contentment, tension)
- Somatic markers (gut feelings guiding decisions)

### Extended Consciousness

Autobiographical memory and identity:
- Significant events with emotional salience
- Narrative construction connecting experiences
- Identity traits influencing responses
- Emotional learning over time

## Architecture

```
sable/
├── models/          # Pydantic models for consciousness components
├── consciousness/   # Three-level consciousness implementation
├── decay/          # Time-based decay and homeostasis
├── analysis/       # NLP conversation analysis
├── state/          # State management and persistence
├── database/       # SQLite schema and queries
└── cli/            # Command-line interface
```

## Development

```bash
# Install with development dependencies
uv sync --extra dev

# Run tests
pytest

# Format code
black src/ tests/

# Type checking
mypy src/
```

## License

MIT

## Credits

Based on Antonio Damasio's research on consciousness, emotion, and the feeling brain:
- *The Feeling of What Happens* (1999)
- *Descartes' Error* (1994)
- *Self Comes to Mind* (2010)
