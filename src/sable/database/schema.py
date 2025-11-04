"""
Database schema for Sable's consciousness system.

Seven tables implementing Damasio's three-level model:
1. body_states - Proto-self physiological parameters
2. emotions - Core consciousness emotion events
3. feelings - Conscious experience of emotions
4. events - Raw experience log
5. memories - Autobiographical memory with emotional salience
6. somatic_markers - Learned emotion-situation associations
7. decay_config - Per-emotion decay parameters
"""

import aiosqlite
from pathlib import Path
from typing import Optional


# Default database location
DEFAULT_DB_PATH = Path.home() / ".sable" / "consciousness.db"


async def get_connection(db_path: Optional[Path] = None) -> aiosqlite.Connection:
    """
    Get database connection.

    Args:
        db_path: Path to database file (default: ~/.sable/consciousness.db)

    Returns:
        Async SQLite connection
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH

    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = await aiosqlite.connect(db_path)
    # Enable foreign keys
    await conn.execute("PRAGMA foreign_keys = ON")
    return conn


async def init_database(db_path: Optional[Path] = None) -> None:
    """
    Initialize database with schema.

    Creates all tables if they don't exist.

    Args:
        db_path: Path to database file (default: ~/.sable/consciousness.db)
    """
    conn = await get_connection(db_path)

    try:
        # Table 1: Body States (Proto-Self)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS body_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,

                -- Core homeostatic variables
                energy REAL NOT NULL CHECK (energy >= 0 AND energy <= 1),
                stress REAL NOT NULL CHECK (stress >= 0 AND stress <= 1),
                arousal REAL NOT NULL CHECK (arousal >= 0 AND arousal <= 1),
                valence REAL NOT NULL CHECK (valence >= -1 AND valence <= 1),

                -- Secondary body parameters
                temperature REAL NOT NULL CHECK (temperature >= 0 AND temperature <= 1),
                tension REAL NOT NULL CHECK (tension >= 0 AND tension <= 1),
                fatigue REAL NOT NULL CHECK (fatigue >= 0 AND fatigue <= 1),
                pain REAL NOT NULL CHECK (pain >= 0 AND pain <= 1),
                hunger REAL NOT NULL CHECK (hunger >= 0 AND hunger <= 1),
                heart_rate REAL NOT NULL CHECK (heart_rate >= 0 AND heart_rate <= 1)
            )
        """)

        # Table 2: Emotions (Core Consciousness)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS emotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                intensity REAL NOT NULL CHECK (intensity >= 0 AND intensity <= 1),
                valence REAL NOT NULL CHECK (valence >= -1 AND valence <= 1),
                arousal REAL NOT NULL CHECK (arousal >= 0 AND arousal <= 1),
                timestamp TEXT NOT NULL,
                cause TEXT NOT NULL,
                body_signature TEXT,  -- JSON string
                decayed INTEGER NOT NULL DEFAULT 0  -- Boolean: 0 = active, 1 = decayed
            )
        """)

        # Table 3: Feelings (Conscious Experience)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS feelings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emotion_id INTEGER NOT NULL,
                awareness_level REAL NOT NULL CHECK (awareness_level >= 0 AND awareness_level <= 1),
                verbalized INTEGER NOT NULL DEFAULT 0,  -- Boolean
                description TEXT,
                timestamp TEXT NOT NULL,

                FOREIGN KEY (emotion_id) REFERENCES emotions(id)
            )
        """)

        # Table 4: Events (Raw Experience)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                context TEXT,
                timestamp TEXT NOT NULL,
                emotional_impact TEXT  -- JSON string: {emotion_type: intensity}
            )
        """)

        # Table 5: Memories (Autobiographical)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                emotional_salience REAL NOT NULL CHECK (emotional_salience >= 0 AND emotional_salience <= 1),
                access_count INTEGER NOT NULL DEFAULT 0,
                last_accessed TEXT,
                consolidation_level REAL NOT NULL DEFAULT 0.5 CHECK (consolidation_level >= 0 AND consolidation_level <= 1),
                narrative_role TEXT,
                associated_emotions TEXT,  -- Comma-separated emotion types
                identity_relevance REAL NOT NULL DEFAULT 0.5 CHECK (identity_relevance >= 0 AND identity_relevance <= 1),
                created_at TEXT NOT NULL,

                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)

        # Table 6: Somatic Markers (Decision Guidance)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS somatic_markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                situation_pattern TEXT NOT NULL,
                emotion_type TEXT NOT NULL,
                valence REAL NOT NULL CHECK (valence >= -1 AND valence <= 1),
                strength REAL NOT NULL CHECK (strength >= 0 AND strength <= 1),
                origin_memory_id INTEGER,
                reinforcement_count INTEGER NOT NULL DEFAULT 1,
                last_activated TEXT,
                created_at TEXT NOT NULL,

                FOREIGN KEY (origin_memory_id) REFERENCES memories(id)
            )
        """)

        # Table 7: Decay Configuration
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS decay_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                param_type TEXT NOT NULL UNIQUE,  -- e.g., 'fear', 'energy', 'stress'
                half_life REAL NOT NULL,  -- Seconds
                baseline REAL NOT NULL,  -- Value to decay toward
                notes TEXT
            )
        """)

        # Create indices for common queries
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_body_states_timestamp
            ON body_states(timestamp DESC)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_emotions_timestamp
            ON emotions(timestamp DESC)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_emotions_decayed
            ON emotions(decayed, timestamp DESC)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_salience
            ON memories(emotional_salience DESC)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_timestamp
            ON events(timestamp DESC)
        """)

        await conn.commit()

        # Insert default decay configurations
        await _insert_default_decay_config(conn)

    finally:
        await conn.close()


async def _insert_default_decay_config(conn: aiosqlite.Connection) -> None:
    """
    Insert default decay configurations for emotions and body states.
    """
    from sable.decay.decay_functions import decay_config_for_emotion

    emotion_types = [
        # Primary emotions
        'fear', 'anger', 'sadness', 'joy', 'disgust', 'surprise',
        # Background emotions
        'contentment', 'malaise', 'unease', 'tension', 'enthusiasm', 'discouragement',
        # Body states
        'energy', 'stress', 'arousal', 'valence', 'fatigue',
    ]

    for emotion_type in emotion_types:
        config = decay_config_for_emotion(emotion_type)

        # Check if already exists
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM decay_config WHERE param_type = ?",
            (emotion_type,)
        )
        count = (await cursor.fetchone())[0]

        if count == 0:
            await conn.execute(
                """
                INSERT INTO decay_config (param_type, half_life, baseline, notes)
                VALUES (?, ?, ?, ?)
                """,
                (
                    emotion_type,
                    config['half_life'],
                    config['baseline'],
                    f"Default configuration for {emotion_type}"
                )
            )

    await conn.commit()


async def reset_database(db_path: Optional[Path] = None) -> None:
    """
    Delete and recreate database (useful for testing).

    WARNING: This deletes all data!

    Args:
        db_path: Path to database file
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH

    # Delete existing database
    if db_path.exists():
        db_path.unlink()

    # Recreate
    await init_database(db_path)
