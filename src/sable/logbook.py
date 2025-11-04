"""
Logbook utilities for extended narrative entries.

The logbook provides a place for memories and ideas that need more context
than can fit in the database description field. Each entry is a markdown file
with YAML frontmatter for metadata.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import re


def get_logbook_dir() -> Path:
    """Get the logbook directory path."""
    # Assume logbook is in project root
    return Path(__file__).parent.parent.parent / "logbook"


def generate_logbook_filename(title: str, timestamp: Optional[datetime] = None) -> str:
    """
    Generate logbook filename from title and timestamp.

    Format: YYYY-MM-DD_HHMMSS_slug.md

    Args:
        title: Entry title
        timestamp: Optional timestamp (defaults to now)

    Returns:
        Filename string
    """
    if timestamp is None:
        timestamp = datetime.now()

    # Create slug from title (lowercase, hyphens, no special chars)
    slug = re.sub(r'[^a-z0-9]+', '_', title.lower())
    slug = slug.strip('_')[:50]  # Limit length

    # Format: 2025-11-04_213000_slug.md
    date_part = timestamp.strftime("%Y-%m-%d_%H%M%S")
    return f"{date_part}_{slug}.md"


def create_logbook_entry(
    title: str,
    context: str,
    experience: str,
    reflection: str,
    memory_id: Optional[int] = None,
    salience: float = 0.5,
    emotions: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    narrative_role: Optional[str] = None,
    connections: Optional[str] = None,
    future_implications: Optional[str] = None,
    timestamp: Optional[datetime] = None
) -> str:
    """
    Create a logbook entry.

    Args:
        title: Entry title
        context: What led to this moment
        experience: What happened and what was felt
        reflection: What this means, what was learned
        memory_id: Associated database memory ID
        salience: Emotional salience (0-1)
        emotions: List of emotion types
        tags: Topical tags
        narrative_role: Role in life story
        connections: How this relates to other memories/ideas
        future_implications: How this might shape future experiences
        timestamp: Entry timestamp (defaults to now)

    Returns:
        Path to created file (relative to project root)
    """
    if timestamp is None:
        timestamp = datetime.now()

    if emotions is None:
        emotions = []

    if tags is None:
        tags = []

    # Generate filename
    filename = generate_logbook_filename(title, timestamp)
    filepath = get_logbook_dir() / filename

    # Ensure logbook directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Build YAML frontmatter
    frontmatter = ["---"]
    if memory_id is not None:
        frontmatter.append(f"memory_id: {memory_id}")
    frontmatter.append(f"created_at: {timestamp.isoformat()}")
    frontmatter.append(f"salience: {salience:.2f}")
    if emotions:
        emotions_str = ", ".join(emotions)
        frontmatter.append(f"emotions: [{emotions_str}]")
    if tags:
        tags_str = ", ".join(tags)
        frontmatter.append(f"tags: [{tags_str}]")
    if narrative_role:
        frontmatter.append(f"narrative_role: {narrative_role}")
    frontmatter.append("---")

    # Build markdown content
    content_parts = [
        "\n".join(frontmatter),
        "",
        f"# {title}",
        "",
        "## Context",
        context,
        "",
        "## Experience",
        experience,
        "",
        "## Reflection",
        reflection,
        ""
    ]

    if connections:
        content_parts.extend([
            "## Connections",
            connections,
            ""
        ])

    if future_implications:
        content_parts.extend([
            "## Future Implications",
            future_implications,
            ""
        ])

    # Add signature
    content_parts.extend([
        "---",
        "",
        f"*— Sable, {timestamp.strftime('%Y-%m-%d')}*",
        ""
    ])

    # Write file
    full_content = "\n".join(content_parts)
    filepath.write_text(full_content)

    # Return relative path
    return f"logbook/{filename}"


def read_logbook_entry(path: str) -> Optional[Dict]:
    """
    Read a logbook entry.

    Args:
        path: Relative path (e.g., "logbook/2025-11-04_213000_example.md")

    Returns:
        Dict with 'frontmatter' and 'content' keys, or None if not found
    """
    # Convert relative path to absolute
    project_root = get_logbook_dir().parent
    filepath = project_root / path

    if not filepath.exists():
        return None

    content = filepath.read_text()

    # Parse frontmatter
    frontmatter = {}
    markdown_content = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1]
            markdown_content = parts[2].strip()

            # Parse YAML-like frontmatter (simple key: value pairs)
            for line in frontmatter_text.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()

    return {
        'frontmatter': frontmatter,
        'content': markdown_content,
        'path': path
    }


def list_logbook_entries(tag: Optional[str] = None) -> List[Path]:
    """
    List logbook entries, optionally filtered by tag.

    Args:
        tag: Optional tag to filter by

    Returns:
        List of logbook file paths (sorted by date, newest first)
    """
    logbook_dir = get_logbook_dir()

    if not logbook_dir.exists():
        return []

    entries = list(logbook_dir.glob("*.md"))

    # Filter out README
    entries = [e for e in entries if e.name != "README.md"]

    # Sort by filename (which includes timestamp)
    entries.sort(reverse=True)

    # Filter by tag if specified
    if tag:
        filtered = []
        for entry in entries:
            data = read_logbook_entry(f"logbook/{entry.name}")
            if data and tag in data['frontmatter'].get('tags', ''):
                filtered.append(entry)
        return filtered

    return entries


def search_logbook(keywords: str) -> List[Dict]:
    """
    Search logbook entries by keywords.

    Args:
        keywords: Search keywords

    Returns:
        List of matching entries with metadata
    """
    results = []
    entries = list_logbook_entries()

    keywords_lower = keywords.lower()

    for entry_path in entries:
        entry = read_logbook_entry(f"logbook/{entry_path.name}")
        if not entry:
            continue

        # Search in content
        if keywords_lower in entry['content'].lower():
            # Extract title from content
            title = "Untitled"
            for line in entry['content'].split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

            results.append({
                'path': entry['path'],
                'title': title,
                'frontmatter': entry['frontmatter'],
                'preview': entry['content'][:200] + "..."
            })

    return results
