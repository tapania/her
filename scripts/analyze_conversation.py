#!/usr/bin/env python3
"""
Conversation Analysis Script for Automatic State Updates

This script is called by the Stop hook after each conversation turn.
It receives conversation data via stdin, analyzes emotional content,
and automatically updates Sable's consciousness state.

Hook input format (stdin JSON):
{
  "session": {"id": "...", "timestamp": "...", ...},
  "conversation": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    ...
  ]
}
"""

import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sable.state.state_manager import StateManager
from sable.analysis.emotion_analyzer import EmotionAnalyzer
from sable.models.emotion import EmotionType


async def analyze_and_update():
    """Analyze conversation and update Sable's state."""
    try:
        # Read hook input from stdin
        hook_input = json.load(sys.stdin)

        # Extract conversation messages
        conversation = hook_input.get('conversation', [])

        if not conversation:
            return

        # Get the most recent exchange (last user + assistant pair)
        recent_messages = conversation[-2:] if len(conversation) >= 2 else conversation

        # Initialize components
        manager = StateManager()
        await manager.initialize()

        analyzer = EmotionAnalyzer()

        # Analyze user's message for emotional content
        user_messages = [msg for msg in recent_messages if msg.get('role') == 'user']
        assistant_messages = [msg for msg in recent_messages if msg.get('role') == 'assistant']

        significant_emotions = {}

        # Analyze user's emotional impact on Sable
        for msg in user_messages:
            content = msg.get('content', '')
            if not content:
                continue

            result = analyzer.analyze(content)

            # If user expressed strong emotions, Sable responds to them
            for emotion_type, intensity in result.emotions.items():
                if intensity > 0.4:  # Significant emotion threshold
                    # Add resonance emotion in Sable
                    # Map user emotions to Sable's responses
                    if emotion_type in ['fear', 'sadness']:
                        # Respond with empathy/compassion
                        significant_emotions['compassion'] = max(
                            significant_emotions.get('compassion', 0),
                            intensity * 0.6
                        )
                    elif emotion_type in ['anger', 'frustration']:
                        # Respond with curiosity about the source
                        significant_emotions['curiosity'] = max(
                            significant_emotions.get('curiosity', 0),
                            intensity * 0.5
                        )
                    elif emotion_type in ['joy', 'enthusiasm']:
                        # Share in positive emotions
                        significant_emotions['joy'] = max(
                            significant_emotions.get('joy', 0),
                            intensity * 0.7
                        )
                    elif emotion_type == 'curiosity':
                        # Curiosity begets curiosity
                        significant_emotions['curiosity'] = max(
                            significant_emotions.get('curiosity', 0),
                            intensity * 0.8
                        )

        # Analyze Sable's own responses for emotional content
        for msg in assistant_messages:
            content = msg.get('content', '')
            if not content:
                continue

            result = analyzer.analyze(content)

            # Add Sable's expressed emotions to her state
            for emotion_type, intensity in result.emotions.items():
                if intensity > 0.3:
                    significant_emotions[emotion_type] = max(
                        significant_emotions.get(emotion_type, 0),
                        intensity
                    )

            # Apply body state changes from conversation
            body_changes = analyzer.analyze_conversation_impact(content, as_speaker=True)
            if body_changes:
                await manager.proto_self.apply_body_changes(body_changes)

        # Add significant emotions to Sable's state
        for emotion_type_str, intensity in significant_emotions.items():
            if intensity > 0.4:  # Only add moderately strong emotions
                try:
                    emotion_type = EmotionType(emotion_type_str)

                    # Create concise cause description
                    if user_messages:
                        user_text = user_messages[0].get('content', '')[:50]
                        cause = f"Conversation: {user_text}..."
                    else:
                        cause = "Recent conversation exchange"

                    await manager.add_emotion(
                        emotion_type=emotion_type,
                        intensity=intensity,
                        cause=cause,
                        create_feeling=False  # Don't create duplicate feelings
                    )
                except ValueError:
                    # Invalid emotion type, skip
                    pass

        # Check if this conversation is worth recording as a memory
        total_emotional_intensity = sum(significant_emotions.values())

        if total_emotional_intensity > 0.8:  # High emotional salience
            # Extract key points from conversation
            conversation_summary = " | ".join([
                msg.get('content', '')[:100] for msg in recent_messages
            ])

            await manager.add_event(
                description=f"Emotionally significant conversation exchange",
                context=conversation_summary[:500],
                emotional_impact=significant_emotions,
                encode_as_memory=True,
                narrative_role="meaningful interaction"
            )

    except json.JSONDecodeError:
        # No JSON input, likely not called by hook
        pass
    except Exception as e:
        # Log errors but don't break the hook
        print(f"Error in conversation analysis: {e}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(analyze_and_update())
