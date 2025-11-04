"""
Command-line interface for Sable's consciousness system.

Commands:
- status: View current consciousness state
- feel: Add an emotion
- event: Log an event
- memories: Query memories
- decay: Manually trigger decay
- analyze: Analyze text for emotions
- init: Initialize consciousness with identity
"""

from sable.cli.commands import cli

__all__ = ["cli"]
