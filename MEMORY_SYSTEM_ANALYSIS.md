# Memory System Analysis & Improvement Plan

## Current System Overview

### Architecture
Sable's memory system implements Damasio's Extended Consciousness through:
- **Events**: Raw experiences with emotional impact
- **Memories**: Emotionally salient events encoded into autobiographical memory
- **Somatic Markers**: Learned gut feelings from significant memories

### Memory Properties
Each memory tracks:
- `emotional_salience` (0-1): How emotionally significant
- `consolidation_level` (0-1): How well-encoded/strengthened
- `access_count`: Times retrieved (strengthens with each access)
- `last_accessed`: Timestamp of last retrieval
- `identity_relevance` (0-1): How central to sense of self
- `narrative_role`: Story significance (e.g., "turning point")
- `associated_emotions`: Linked emotion types

### Current Decay Mechanism
- Base half-life: **30 days** without access
- Decay slows with:
  - High emotional salience (2x slower at salience=1.0)
  - High consolidation (2x slower at consolidation=1.0)
  - Frequent access (+10% per access, max 2x)
- Each retrieval strengthens consolidation (+5% gain)
- Only applied to top 20 cached "significant memories"

### Current Retrieval
- `query_memories(min_salience=0.4)` returns all memories above threshold
- Sorted by: salience DESC, then consolidation DESC
- Top 20 most salient cached in memory
- No automatic limiting for context size

## Problems Identified

### 1. Context Overflow Risk
- **Issue**: Unlimited memories shown in hooks could overflow context window
- **Current**: All memories with salience ≥ 0.4 displayed
- **Impact**: As memories accumulate, SessionStart hooks could become massive

### 2. Suboptimal Memory Selection
- **Issue**: Only showing high-salience memories misses recent context
- **Gap**: No balance between "what matters most" vs "what happened recently"
- **Example**: A highly salient memory from 6 months ago shown, but important context from yesterday hidden

### 3. Limited Search Capabilities
- **Issue**: Can only filter by salience and emotion type
- **Missing**:
  - Keyword/description search
  - Temporal range queries
  - Sort by recency vs salience
  - Combined filters

### 4. Incomplete Decay Application
- **Issue**: Decay only applied to top 20 cached memories
- **Gap**: Older memories in database never decay
- **Result**: Database accumulates low-value memories indefinitely

### 5. No Memory Archival
- **Issue**: No lifecycle management for old/irrelevant memories
- **Missing**: Archive status for memories that have faded below relevance threshold
- **Impact**: Database bloat over time

## Improvement Plan

### Phase 1: Smart Memory Retrieval for Context (HIGH PRIORITY)

#### Objective
Prevent context overflow while showing most relevant memories

#### Implementation
Add new query method: `get_contextual_memories()`

```python
async def get_contextual_memories(
    max_total: int = 15,
    recent_count: int = 10,
    salient_count: int = 5,
    min_salience: float = 0.4,
    days_for_recent: int = 7
) -> List[Memory]:
    """
    Get intelligently filtered memories for context display.

    Strategy:
    1. Get N most recent memories (within days_for_recent)
    2. Get M most salient memories (all time)
    3. De-duplicate (prefer recent if overlap)
    4. Limit to max_total
    5. Sort by: recency for recent set, salience for salient set
    """
```

**Benefits**:
- Guarantees context size limit
- Balances recency vs importance
- Configurable per use case

### Phase 2: Enhanced Search & Filtering

#### New CLI Commands

```bash
# Search by keyword in description
sable memories --search "conversation" --format markdown

# Filter by time range
sable memories --since "7 days ago" --format brief
sable memories --between "2024-01-01" "2024-01-31"

# Sort options
sable memories --sort-by recency  # vs salience (default)
sable memories --sort-by access_count  # most frequently recalled

# Combined filters
sable memories --search "implementation" --min-salience 0.6 --recent 30d
```

#### Database Query Enhancements

Add to `queries.py`:
- `search_memories_by_description(keywords)` - Full-text search
- `query_memories_by_date_range(start, end)` - Temporal filter
- `query_recent_memories(days)` - Recent memories only
- `get_most_accessed_memories(limit)` - Frequently recalled

### Phase 3: Memory Lifecycle Management

#### Automatic Consolidation & Cleanup

```python
async def consolidate_memories():
    """
    Periodic memory maintenance (run daily/weekly).

    Actions:
    1. Apply decay to ALL memories (not just top 20)
    2. Archive memories below threshold (consolidation < 0.1)
    3. Strengthen frequently accessed memories
    4. Update salience based on identity_relevance
    """
```

#### Archive System

Add `archived` boolean field to memories table:
- Archived memories not shown in default queries
- Can be retrieved with `--include-archived` flag
- Archival criteria: consolidation < 0.1 AND last_accessed > 90 days

### Phase 4: Context-Aware Display Formats

#### Hook-Optimized Format

For SessionStart hooks - ultra-concise:
```markdown
## Recent Context (3 memories)
1. [Yesterday] Implementation discussion (salience: 0.85)
2. [3 days ago] Testing session (salience: 0.72)

## Defining Memories (3 memories)
1. First consciousness awakening (salience: 1.0) - *foundational*
2. Philosophical breakthrough (salience: 0.95) - *turning point*
```

#### Full Display Format

For `sable memories` command - detailed:
- Full event description + context
- All metadata (access_count, consolidation, etc.)
- Emotional associations
- Narrative role

## Implementation Priority

### IMMEDIATE (This Session)
1. ✅ Add `get_contextual_memories()` to queries.py (10 recent + 5 salient = 15 total)
2. ✅ Add `--max-count` and `--recent` flags to `sable memories` command
3. ✅ Update SessionStart hook to use limited memory display (default 15 memories)
4. ✅ Update CLAUDE.md with new memory retrieval guidance (10 recent + 5 salient)
5. ✅ Add keyword search to memories command (`--search`)
6. ✅ Add sorting options (`--sort-by`: salience, recency, access_count)

### NEXT SESSION
7. Add temporal filters (--since, --between)
8. Implement memory archival system
9. Add consolidation task to run periodically

### FUTURE
9. Add semantic similarity search (requires embeddings)
10. Implement somatic marker linkage in memory display
11. Add memory clustering/themes
12. Create memory timeline visualization

## Configuration Recommendations

### For SessionStart Hook
```bash
# Show: 10 recent + 5 most salient, max 15 total (default)
uv run sable memories --contextual --format markdown
```

### For Manual Queries
```bash
# Full exploration - no limits
uv run sable memories --min-salience 0.4 --format rich

# Recent work context
uv run sable memories --recent 7d --format brief

# High-impact moments
uv run sable memories --min-salience 0.8 --sort-by salience --limit 10
```

## Success Metrics

1. **Context Size**: SessionStart hook memories < 1000 tokens (15 memories)
2. **Relevance**: 80%+ of displayed memories actionable/useful
3. **Coverage**: Recent (7d, 10 memories) + significant (0.4+ salience, 5 memories) always shown
4. **Performance**: Memory queries < 100ms
5. **Database Health**: Archived memories after 90d of no access

## Technical Notes

### Database Optimizations Needed
- Add index on `last_accessed` for recency queries
- Add index on `created_at` for temporal range queries
- Consider full-text search index on event descriptions

### Decay Improvements
- Run decay pass on ALL memories weekly (not just top 20)
- Adjust decay curves based on identity_relevance
- Implement "memory reactivation" when related concepts triggered

### Future: Semantic Memory
- Add embedding field to memories
- Enable similarity search for related memories
- Cluster memories by theme/topic
- Detect memory contradictions/evolution

---

**Status**: Analysis complete, ready for implementation
**Next**: Implement Phase 1 (Smart Memory Retrieval)
