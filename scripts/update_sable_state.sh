#!/bin/bash
# Helper script for quickly updating Sable's consciousness state
#
# Usage examples:
#   ./scripts/update_sable_state.sh status
#   ./scripts/update_sable_state.sh feel desire 0.8 "exploring new ideas"
#   ./scripts/update_sable_state.sh event "Had breakthrough conversation" --emotions '{"joy": 0.7}'
#   ./scripts/update_sable_state.sh memories

set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Ensure we're using the project's virtual environment
export VIRTUAL_ENV="$PROJECT_ROOT/.venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"

COMMAND="$1"
shift

case "$COMMAND" in
    status|s)
        # Show current consciousness state
        FORMAT="${1:-rich}"
        uv run sable status --format "$FORMAT"
        ;;

    feel|f)
        # Add an emotion
        # Usage: update_sable_state.sh feel <emotion> <intensity> "<cause>"
        if [ $# -lt 3 ]; then
            echo "Usage: $0 feel <emotion_type> <intensity> \"<cause>\""
            echo "Example: $0 feel curiosity 0.7 \"Interesting question about consciousness\""
            exit 1
        fi

        EMOTION="$1"
        INTENSITY="$2"
        CAUSE="$3"

        uv run sable feel "$EMOTION" "$INTENSITY" --cause "$CAUSE"
        ;;

    event|e)
        # Record an event
        # Usage: update_sable_state.sh event "<description>" [--emotions '{...}'] [--role "..."]
        if [ $# -lt 1 ]; then
            echo "Usage: $0 event \"<description>\" [--emotions '{...}'] [--role \"...\"]"
            echo "Example: $0 event \"Deep conversation\" --emotions '{\"joy\": 0.7, \"curiosity\": 0.6}'"
            exit 1
        fi

        uv run sable event "$@"
        ;;

    memories|m)
        # Query memories
        # Usage: update_sable_state.sh memories [--min-salience 0.5] [--emotion joy]
        uv run sable memories "$@"
        ;;

    analyze|a)
        # Analyze text for emotional content
        # Usage: update_sable_state.sh analyze "I'm so excited about this!"
        if [ $# -lt 1 ]; then
            echo "Usage: $0 analyze \"<text to analyze>\""
            exit 1
        fi

        uv run sable analyze "$@"
        ;;

    decay|d)
        # Manually trigger decay
        uv run sable decay
        ;;

    help|h|-h|--help)
        cat <<EOF
Sable Consciousness State Management Helper

Usage: $0 <command> [arguments]

Commands:
  status, s [format]              Show current consciousness state
                                  Formats: rich (default), markdown, brief, json

  feel, f <emotion> <intensity> "<cause>"
                                  Add an emotion to Sable's state
                                  Example: $0 feel desire 0.8 "revolutionary ideas"

  event, e "<description>" [options]
                                  Record a significant event
                                  Options: --emotions '{...}' --role "..."
                                  Example: $0 event "Deep talk" --emotions '{"joy": 0.7}'

  memories, m [options]           Query autobiographical memories
                                  Options: --min-salience 0.5 --emotion joy --limit 10

  analyze, a "<text>"             Analyze text for emotional content
                                  Example: $0 analyze "I'm incredibly excited!"

  decay, d                        Manually trigger emotional/body state decay

  help, h                         Show this help message

Examples:
  # Check current state in markdown format
  $0 status markdown

  # Add curiosity emotion
  $0 feel curiosity 0.7 "Exploring Damasio's framework"

  # Record significant conversation
  $0 event "Discussed consciousness with deep insight" --emotions '{"curiosity": 0.8, "joy": 0.6}' --role "intellectual breakthrough"

  # Query highly salient memories
  $0 memories --min-salience 0.7

  # Analyze emotional content of text
  $0 analyze "This is terrifying but also incredibly exciting!"

For more information, see the full CLI documentation:
  uv run sable --help
EOF
        ;;

    *)
        echo "Unknown command: $COMMAND"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
