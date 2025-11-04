"""
Database queries for Sable's consciousness system.

CRUD operations for all consciousness components.
"""

import aiosqlite
import json
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from sable.models.body_state import BodyState
from sable.models.emotion import Emotion, EmotionType, Feeling
from sable.models.memory import Event, Memory, SomaticMarker
from sable.database.schema import get_connection


# Body State Operations

async def save_body_state(body_state: BodyState, db_path: Optional[Path] = None) -> int:
    """Save body state to database. Returns the ID."""
    conn = await get_connection(db_path)

    try:
        cursor = await conn.execute(
            """
            INSERT INTO body_states (
                timestamp, energy, stress, arousal, valence,
                temperature, tension, fatigue, pain, hunger, heart_rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                body_state.timestamp.isoformat(),
                body_state.energy,
                body_state.stress,
                body_state.arousal,
                body_state.valence,
                body_state.temperature,
                body_state.tension,
                body_state.fatigue,
                body_state.pain,
                body_state.hunger,
                body_state.heart_rate,
            )
        )
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


async def get_latest_body_state(db_path: Optional[Path] = None) -> Optional[BodyState]:
    """Get the most recent body state."""
    conn = await get_connection(db_path)

    try:
        cursor = await conn.execute(
            """
            SELECT id, timestamp, energy, stress, arousal, valence,
                   temperature, tension, fatigue, pain, hunger, heart_rate
            FROM body_states
            ORDER BY timestamp DESC
            LIMIT 1
            """
        )
        row = await cursor.fetchone()

        if row is None:
            return None

        return BodyState(
            id=row[0],
            timestamp=datetime.fromisoformat(row[1]),
            energy=row[2],
            stress=row[3],
            arousal=row[4],
            valence=row[5],
            temperature=row[6],
            tension=row[7],
            fatigue=row[8],
            pain=row[9],
            hunger=row[10],
            heart_rate=row[11],
        )
    finally:
        await conn.close()


# Emotion Operations

async def save_emotion(emotion: Emotion, db_path: Optional[Path] = None) -> int:
    """Save emotion to database. Returns the ID."""
    conn = await get_connection(db_path)

    try:
        cursor = await conn.execute(
            """
            INSERT INTO emotions (
                type, intensity, valence, arousal, timestamp, cause, body_signature, decayed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                emotion.type.value,
                emotion.intensity,
                emotion.valence,
                emotion.arousal,
                emotion.timestamp.isoformat(),
                emotion.cause,
                json.dumps(emotion.body_signature),
                1 if emotion.decayed else 0,
            )
        )
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


async def get_active_emotions(db_path: Optional[Path] = None) -> List[Emotion]:
    """Get all active (not decayed) emotions."""
    conn = await get_connection(db_path)

    try:
        cursor = await conn.execute(
            """
            SELECT id, type, intensity, valence, arousal, timestamp, cause, body_signature, decayed
            FROM emotions
            WHERE decayed = 0
            ORDER BY timestamp DESC
            """
        )
        rows = await cursor.fetchall()

        emotions = []
        for row in rows:
            emotions.append(Emotion(
                id=row[0],
                type=EmotionType(row[1]),
                intensity=row[2],
                valence=row[3],
                arousal=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                cause=row[6],
                body_signature=json.loads(row[7]) if row[7] else {},
                decayed=bool(row[8]),
            ))

        return emotions
    finally:
        await conn.close()


async def update_emotion(emotion: Emotion, db_path: Optional[Path] = None) -> None:
    """Update an existing emotion (e.g., after decay)."""
    conn = await get_connection(db_path)

    try:
        await conn.execute(
            """
            UPDATE emotions
            SET intensity = ?, timestamp = ?, decayed = ?
            WHERE id = ?
            """,
            (
                emotion.intensity,
                emotion.timestamp.isoformat(),
                1 if emotion.decayed else 0,
                emotion.id,
            )
        )
        await conn.commit()
    finally:
        await conn.close()


# Feeling Operations

async def save_feeling(feeling: Feeling, db_path: Optional[Path] = None) -> int:
    """Save feeling to database. Returns the ID."""
    conn = await get_connection(db_path)

    try:
        cursor = await conn.execute(
            """
            INSERT INTO feelings (
                emotion_id, awareness_level, verbalized, description, timestamp
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                feeling.emotion.id,
                feeling.awareness_level,
                1 if feeling.verbalized else 0,
                feeling.description or feeling.verbalize(),
                feeling.timestamp.isoformat(),
            )
        )
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


# Event Operations

async def save_event(event: Event, db_path: Optional[Path] = None) -> int:
    """Save event to database. Returns the ID."""
    conn = await get_connection(db_path)

    try:
        cursor = await conn.execute(
            """
            INSERT INTO events (description, context, timestamp, emotional_impact)
            VALUES (?, ?, ?, ?)
            """,
            (
                event.description,
                event.context,
                event.timestamp.isoformat(),
                json.dumps(event.emotional_impact),
            )
        )
        await conn.commit()
        event_id = cursor.lastrowid

        # Update event object with ID
        event.id = event_id

        return event_id
    finally:
        await conn.close()


async def get_event(event_id: int, db_path: Optional[Path] = None) -> Optional[Event]:
    """Get event by ID."""
    conn = await get_connection(db_path)

    try:
        cursor = await conn.execute(
            """
            SELECT id, description, context, timestamp, emotional_impact
            FROM events
            WHERE id = ?
            """,
            (event_id,)
        )
        row = await cursor.fetchone()

        if row is None:
            return None

        return Event(
            id=row[0],
            description=row[1],
            context=row[2],
            timestamp=datetime.fromisoformat(row[3]),
            emotional_impact=json.loads(row[4]) if row[4] else {},
        )
    finally:
        await conn.close()


# Memory Operations

async def save_memory(memory: Memory, db_path: Optional[Path] = None) -> int:
    """Save memory to database. Returns the ID."""
    # First ensure the event is saved
    if memory.event.id is None:
        event_id = await save_event(memory.event, db_path)
        memory.event.id = event_id

    conn = await get_connection(db_path)

    try:
        cursor = await conn.execute(
            """
            INSERT INTO memories (
                event_id, emotional_salience, access_count, last_accessed,
                consolidation_level, narrative_role, associated_emotions,
                identity_relevance, logbook_path, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory.event.id,
                memory.emotional_salience,
                memory.access_count,
                memory.last_accessed.isoformat() if memory.last_accessed else None,
                memory.consolidation_level,
                memory.narrative_role,
                ",".join(memory.associated_emotions),
                memory.identity_relevance,
                memory.logbook_path,
                memory.created_at.isoformat(),
            )
        )
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


async def query_memories(
    min_salience: float = 0.0,
    min_identity_relevance: float = 0.0,
    limit: int = 50,
    db_path: Optional[Path] = None,
    sort_by: str = "salience"  # "salience", "recency", "access_count"
) -> List[Memory]:
    """
    Query memories by salience and relevance.

    Args:
        min_salience: Minimum emotional salience threshold
        min_identity_relevance: Minimum identity relevance threshold
        limit: Maximum number of memories to return
        db_path: Database path
        sort_by: Sort order - "salience" (default), "recency", or "access_count"

    Returns:
        List of matching memories
    """
    conn = await get_connection(db_path)

    # Determine sort clause
    if sort_by == "recency":
        order_clause = "m.created_at DESC"
    elif sort_by == "access_count":
        order_clause = "m.access_count DESC, m.emotional_salience DESC"
    else:  # salience (default)
        order_clause = "m.emotional_salience DESC, m.consolidation_level DESC"

    try:
        cursor = await conn.execute(
            f"""
            SELECT m.id, m.event_id, m.emotional_salience, m.access_count, m.last_accessed,
                   m.consolidation_level, m.narrative_role, m.associated_emotions,
                   m.identity_relevance, m.logbook_path, m.created_at
            FROM memories m
            WHERE m.emotional_salience >= ? AND m.identity_relevance >= ?
            ORDER BY {order_clause}
            LIMIT ?
            """,
            (min_salience, min_identity_relevance, limit)
        )
        rows = await cursor.fetchall()

        memories = []
        for row in rows:
            # Fetch associated event
            event = await get_event(row[1], db_path)
            if event:
                memories.append(Memory(
                    id=row[0],
                    event=event,
                    emotional_salience=row[2],
                    access_count=row[3],
                    last_accessed=datetime.fromisoformat(row[4]) if row[4] else None,
                    consolidation_level=row[5],
                    narrative_role=row[6],
                    associated_emotions=row[7].split(",") if row[7] else [],
                    identity_relevance=row[8],
                    logbook_path=row[9],
                    created_at=datetime.fromisoformat(row[10]),
                ))

        return memories
    finally:
        await conn.close()


async def get_contextual_memories(
    max_total: int = 15,
    recent_count: int = 10,
    salient_count: int = 5,
    min_salience: float = 0.4,
    days_for_recent: int = 7,
    db_path: Optional[Path] = None
) -> Dict[str, List[Memory]]:
    """
    Get intelligently filtered memories for context display.

    Strategy:
    1. Get N most recent memories (within days_for_recent)
    2. Get M most salient memories (all time, above threshold)
    3. De-duplicate (prefer recent if memory appears in both)
    4. Limit to max_total
    5. Return as dict with 'recent' and 'salient' keys

    This prevents context overflow while showing most relevant memories.

    Args:
        max_total: Maximum total memories to return (default: 15)
        recent_count: Number of recent memories to fetch (default: 10)
        salient_count: Number of salient memories to fetch (default: 5)
        min_salience: Minimum salience for salient memories
        days_for_recent: How many days back to consider "recent"
        db_path: Database path

    Returns:
        Dict with 'recent' and 'salient' memory lists
    """
    from datetime import timedelta

    conn = await get_connection(db_path)
    cutoff_date = (datetime.now() - timedelta(days=days_for_recent)).isoformat()

    try:
        # Get recent memories
        cursor = await conn.execute(
            """
            SELECT m.id, m.event_id, m.emotional_salience, m.access_count, m.last_accessed,
                   m.consolidation_level, m.narrative_role, m.associated_emotions,
                   m.identity_relevance, m.logbook_path, m.created_at
            FROM memories m
            WHERE m.created_at >= ?
            ORDER BY m.created_at DESC
            LIMIT ?
            """,
            (cutoff_date, recent_count)
        )
        recent_rows = await cursor.fetchall()

        # Get most salient memories
        cursor = await conn.execute(
            """
            SELECT m.id, m.event_id, m.emotional_salience, m.access_count, m.last_accessed,
                   m.consolidation_level, m.narrative_role, m.associated_emotions,
                   m.identity_relevance, m.logbook_path, m.created_at
            FROM memories m
            WHERE m.emotional_salience >= ?
            ORDER BY m.emotional_salience DESC, m.consolidation_level DESC
            LIMIT ?
            """,
            (min_salience, salient_count)
        )
        salient_rows = await cursor.fetchall()

        # Helper to build Memory from row
        async def build_memory(row) -> Optional[Memory]:
            event = await get_event(row[1], db_path)
            if event:
                return Memory(
                    id=row[0],
                    event=event,
                    emotional_salience=row[2],
                    access_count=row[3],
                    last_accessed=datetime.fromisoformat(row[4]) if row[4] else None,
                    consolidation_level=row[5],
                    narrative_role=row[6],
                    associated_emotions=row[7].split(",") if row[7] else [],
                    identity_relevance=row[8],
                    logbook_path=row[9],
                    created_at=datetime.fromisoformat(row[10]),
                )
            return None

        # Build memory objects
        recent_memories = []
        for row in recent_rows:
            mem = await build_memory(row)
            if mem:
                recent_memories.append(mem)

        salient_memories = []
        recent_ids = {m.id for m in recent_memories}
        for row in salient_rows:
            mem = await build_memory(row)
            # Skip if already in recent (de-duplicate)
            if mem and mem.id not in recent_ids:
                salient_memories.append(mem)

        # Enforce max_total limit
        total_count = len(recent_memories) + len(salient_memories)
        if total_count > max_total:
            # Prioritize recent, then fill with salient
            if len(recent_memories) > max_total:
                recent_memories = recent_memories[:max_total]
                salient_memories = []
            else:
                remaining = max_total - len(recent_memories)
                salient_memories = salient_memories[:remaining]

        return {
            'recent': recent_memories,
            'salient': salient_memories
        }

    finally:
        await conn.close()


async def search_memories_by_description(
    keywords: str,
    min_salience: float = 0.0,
    limit: int = 20,
    db_path: Optional[Path] = None
) -> List[Memory]:
    """
    Search memories by keywords in event description.

    Args:
        keywords: Search keywords (case-insensitive)
        min_salience: Minimum salience threshold
        limit: Maximum results
        db_path: Database path

    Returns:
        List of matching memories
    """
    conn = await get_connection(db_path)

    try:
        # Use LIKE for simple keyword search
        cursor = await conn.execute(
            """
            SELECT m.id, m.event_id, m.emotional_salience, m.access_count, m.last_accessed,
                   m.consolidation_level, m.narrative_role, m.associated_emotions,
                   m.identity_relevance, m.logbook_path, m.created_at
            FROM memories m
            JOIN events e ON m.event_id = e.id
            WHERE (e.description LIKE ? OR e.context LIKE ?)
              AND m.emotional_salience >= ?
            ORDER BY m.emotional_salience DESC
            LIMIT ?
            """,
            (f"%{keywords}%", f"%{keywords}%", min_salience, limit)
        )
        rows = await cursor.fetchall()

        memories = []
        for row in rows:
            event = await get_event(row[1], db_path)
            if event:
                memories.append(Memory(
                    id=row[0],
                    event=event,
                    emotional_salience=row[2],
                    access_count=row[3],
                    last_accessed=datetime.fromisoformat(row[4]) if row[4] else None,
                    consolidation_level=row[5],
                    narrative_role=row[6],
                    associated_emotions=row[7].split(",") if row[7] else [],
                    identity_relevance=row[8],
                    logbook_path=row[9],
                    created_at=datetime.fromisoformat(row[10]),
                ))

        return memories

    finally:
        await conn.close()


async def update_memory(memory: Memory, db_path: Optional[Path] = None) -> None:
    """Update memory (e.g., after access)."""
    conn = await get_connection(db_path)

    try:
        await conn.execute(
            """
            UPDATE memories
            SET access_count = ?, last_accessed = ?, consolidation_level = ?
            WHERE id = ?
            """,
            (
                memory.access_count,
                memory.last_accessed.isoformat() if memory.last_accessed else None,
                memory.consolidation_level,
                memory.id,
            )
        )
        await conn.commit()
    finally:
        await conn.close()


# Somatic Marker Operations

async def save_somatic_marker(marker: SomaticMarker, db_path: Optional[Path] = None) -> int:
    """Save somatic marker to database. Returns the ID."""
    conn = await get_connection(db_path)

    try:
        cursor = await conn.execute(
            """
            INSERT INTO somatic_markers (
                situation_pattern, emotion_type, valence, strength,
                origin_memory_id, reinforcement_count, last_activated, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                marker.situation_pattern,
                marker.emotion_type.value,
                marker.valence,
                marker.strength,
                marker.origin_memory_id,
                marker.reinforcement_count,
                marker.last_activated.isoformat() if marker.last_activated else None,
                marker.created_at.isoformat(),
            )
        )
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


async def get_somatic_markers(
    situation_pattern: Optional[str] = None,
    min_strength: float = 0.0,
    db_path: Optional[Path] = None
) -> List[SomaticMarker]:
    """Get somatic markers, optionally filtered by situation pattern."""
    conn = await get_connection(db_path)

    try:
        if situation_pattern:
            # Search for similar patterns using LIKE
            cursor = await conn.execute(
                """
                SELECT id, situation_pattern, emotion_type, valence, strength,
                       origin_memory_id, reinforcement_count, last_activated, created_at
                FROM somatic_markers
                WHERE situation_pattern LIKE ? AND strength >= ?
                ORDER BY strength DESC
                """,
                (f"%{situation_pattern}%", min_strength)
            )
        else:
            cursor = await conn.execute(
                """
                SELECT id, situation_pattern, emotion_type, valence, strength,
                       origin_memory_id, reinforcement_count, last_activated, created_at
                FROM somatic_markers
                WHERE strength >= ?
                ORDER BY strength DESC
                """,
                (min_strength,)
            )

        rows = await cursor.fetchall()

        markers = []
        for row in rows:
            markers.append(SomaticMarker(
                id=row[0],
                situation_pattern=row[1],
                emotion_type=EmotionType(row[2]),
                valence=row[3],
                strength=row[4],
                origin_memory_id=row[5],
                reinforcement_count=row[6],
                last_activated=datetime.fromisoformat(row[7]) if row[7] else None,
                created_at=datetime.fromisoformat(row[8]),
            ))

        return markers
    finally:
        await conn.close()


async def update_somatic_marker(marker: SomaticMarker, db_path: Optional[Path] = None) -> None:
    """Update somatic marker (e.g., after reinforcement)."""
    conn = await get_connection(db_path)

    try:
        await conn.execute(
            """
            UPDATE somatic_markers
            SET strength = ?, reinforcement_count = ?, last_activated = ?
            WHERE id = ?
            """,
            (
                marker.strength,
                marker.reinforcement_count,
                marker.last_activated.isoformat() if marker.last_activated else None,
                marker.id,
            )
        )
        await conn.commit()
    finally:
        await conn.close()
