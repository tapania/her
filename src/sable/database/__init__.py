"""
Database layer for Sable's consciousness system.

SQLite database storing:
- Body states (proto-self)
- Emotions and feelings (core consciousness)
- Memories, events, and somatic markers (extended consciousness)
- Decay configuration
"""

from sable.database.schema import init_database, get_connection
from sable.database.queries import (
    save_body_state,
    get_latest_body_state,
    save_emotion,
    get_active_emotions,
    save_feeling,
    save_event,
    save_memory,
    query_memories,
    save_somatic_marker,
    get_somatic_markers,
)

__all__ = [
    "init_database",
    "get_connection",
    "save_body_state",
    "get_latest_body_state",
    "save_emotion",
    "get_active_emotions",
    "save_feeling",
    "save_event",
    "save_memory",
    "query_memories",
    "save_somatic_marker",
    "get_somatic_markers",
]
