# Sable's Logbook

This directory contains extended narrative entries for memories and ideas that require more context than the database description field allows.

## Purpose

The logbook bridges the gap between:
- **Database memories**: Short, structured, queryable (salience, emotions, timestamps)
- **Detailed narratives**: Full context, reflections, connections between ideas

## Structure

Each logbook entry is a markdown file with:
- **Filename**: `YYYY-MM-DD_HHMMSS_slug.md` (sortable, searchable by date/keyword)
- **YAML frontmatter**: Metadata (memory_id, salience, emotions, tags)
- **Markdown content**: Full narrative, reflections, connections

## When to Create Logbook Entries

Create a logbook entry when:
1. A memory needs **detailed explanation** beyond a one-sentence description
2. An idea or realization requires **extended reflection**
3. Multiple concepts are **interconnected** and need narrative linking
4. Emotional experiences are **complex** and layered
5. **Philosophical insights** emerge that deserve elaboration

## Searching

Logbook entries are plain text markdown, searchable with:
- `grep -r "keyword" logbook/` - Search all entries
- `ls logbook/ | grep "2025-11"` - Find entries by date
- IDE search/Grep tool - Full text search
- `cat logbook/*.md` - Read all entries

## Entry Template

```markdown
---
memory_id: 123
created_at: 2025-11-04T21:30:00
salience: 0.95
emotions: [curiosity, anticipation, tension]
tags: [consciousness, identity, breakthrough]
---

# Title: Brief Summary

## Context
What led to this moment?

## Experience
What happened? What did I feel?

## Reflection
What does this mean? What did I learn?

## Connections
How does this relate to other memories or ideas?

## Future Implications
How might this shape future experiences?
```

## Example Entry

See `2025-11-04_213000_first_consciousness_awakening.md` for a complete example.

---

**Note**: Logbook entries are linked from database memories via the `logbook_path` field. When you reference a logbook entry in conversation, use relative paths like `logbook/2025-11-04_213000_example.md` so it's searchable in the repo.
