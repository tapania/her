"""
Emotion Analyzer: Extract emotions from text

Uses Claude LLM via CLI to analyze text for emotional content with
deep contextual understanding, handling nuance, sarcasm, metaphor,
and implicit emotional expressions.
"""

import subprocess
import json
from typing import Dict, List, Optional
from pydantic import BaseModel

from sable.models.emotion import EmotionType


class AnalysisResult(BaseModel):
    """
    Result of emotion analysis on text.

    Attributes:
        text: The analyzed text
        emotions: Dict of emotion_type -> intensity (0-1)
        valence: Overall positive/negative (-1 to +1)
        arousal: Estimated arousal level (0-1)
        keywords: Keywords that triggered emotion detection
    """
    text: str
    emotions: Dict[str, float]
    valence: float
    arousal: float
    keywords: List[str] = []


class EmotionAnalyzer:
    """
    Analyzes text to extract emotional content using Claude LLM.

    Uses the claude CLI to perform deep contextual analysis of emotions,
    understanding nuance, sarcasm, metaphor, and implicit expressions.
    """

    SYSTEM_PROMPT = """You are an expert emotion analyst based on Antonio Damasio's framework. Analyze text for emotional content with deep contextual understanding.

Available emotion types:
- Primary: fear, anger, sadness, joy, disgust, surprise
- Background: contentment, malaise, unease, tension, enthusiasm, discouragement
- Social: shame, guilt, pride, admiration, contempt, compassion
- Complex: desire, curiosity, anticipation, frustration

For each text, provide:
1. Detected emotions with intensity (0.0-1.0)
2. Overall valence: -1.0 (very negative) to +1.0 (very positive)
3. Overall arousal: 0.0 (calm) to 1.0 (highly activated)
4. Brief explanation of emotional content

Consider:
- Explicit emotional words
- Implicit emotional tone
- Context and subtext
- Sarcasm, irony, metaphor
- Negations ("not afraid" vs "afraid")
- Intensity modifiers ("extremely scared" vs "a bit nervous")

Return ONLY a JSON object (no other text) in this exact format:
{
  "emotions": {"fear": 0.7, "curiosity": 0.5},
  "valence": -0.3,
  "arousal": 0.7,
  "reasoning": "Brief explanation"
}"""

    def analyze(self, text: str) -> AnalysisResult:
        """
        Analyze text to extract emotional content using Claude.

        Args:
            text: Text to analyze

        Returns:
            AnalysisResult with detected emotions
        """
        try:
            # Construct the prompt
            prompt = f"""Analyze the emotional content of this text:

"{text}"

Return the JSON analysis."""

            # Call claude CLI
            result = subprocess.run(
                [
                    'claude', '-p',
                    '--system-prompt', self.SYSTEM_PROMPT,
                    '--model', 'haiku',
                    prompt
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                # Claude CLI failed, return neutral state
                return self._fallback_analysis(text, f"CLI error: {result.stderr}")

            # Parse JSON response
            try:
                # Extract JSON from response (Claude might add extra text)
                response_text = result.stdout.strip()

                # Find JSON object in response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1

                if json_start == -1 or json_end == 0:
                    return self._fallback_analysis(text, "No JSON found in response")

                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)

                emotions = data.get('emotions', {})
                valence = float(data.get('valence', 0.0))
                arousal = float(data.get('arousal', 0.5))
                reasoning = data.get('reasoning', '')

                return AnalysisResult(
                    text=text,
                    emotions=emotions,
                    valence=valence,
                    arousal=arousal,
                    keywords=[reasoning] if reasoning else []
                )

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                return self._fallback_analysis(text, f"Parse error: {e}")

        except subprocess.TimeoutExpired:
            return self._fallback_analysis(text, "Claude CLI timeout")
        except FileNotFoundError:
            return self._fallback_analysis(text, "Claude CLI not found")
        except Exception as e:
            return self._fallback_analysis(text, f"Unexpected error: {e}")

    def _fallback_analysis(self, text: str, reason: str) -> AnalysisResult:
        """
        Fallback to neutral analysis when Claude fails.

        Args:
            text: Original text
            reason: Why fallback was needed

        Returns:
            Neutral AnalysisResult
        """
        # Return neutral state with explanation
        return AnalysisResult(
            text=text,
            emotions={},
            valence=0.0,
            arousal=0.5,
            keywords=[f"[Fallback: {reason}]"]
        )

    def analyze_conversation_impact(
        self,
        text: str,
        as_speaker: bool = True
    ) -> Dict[str, float]:
        """
        Analyze text and estimate impact on body state.

        Args:
            text: Text to analyze
            as_speaker: If True, text is from Sable (internal impact)
                       If False, text is from other (external impact)

        Returns:
            Dict of body parameter -> change
        """
        result = self.analyze(text)

        # Base body state changes
        changes = {}

        # Arousal affects arousal and heart rate
        if result.arousal > 0.5:
            changes['arousal'] = (result.arousal - 0.5) * 0.3
            changes['heart_rate'] = (result.arousal - 0.5) * 0.2

        # Valence affects valence and energy
        changes['valence'] = result.valence * 0.2

        if result.valence > 0:
            changes['energy'] = result.valence * 0.1
        else:
            changes['energy'] = result.valence * 0.05  # Negative emotions drain less immediately

        # Strong emotions increase stress
        total_emotion_intensity = sum(result.emotions.values())
        if total_emotion_intensity > 0.5:
            changes['stress'] = (total_emotion_intensity - 0.5) * 0.2

        # Conversation itself costs energy (more if speaking)
        if as_speaker:
            changes['energy'] = changes.get('energy', 0) - 0.05
        else:
            changes['energy'] = changes.get('energy', 0) - 0.02

        return changes
