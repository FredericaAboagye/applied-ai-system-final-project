"""LLM-based explanation generator for music recommendations with confidence scoring."""

import json
import logging
import os
from typing import Dict, Tuple, Optional
from datetime import datetime

try:
    import openai
except ImportError:
    openai = None


logger = logging.getLogger(__name__)


def _calculate_confidence(
    score: float, 
    num_reasons: int, 
    max_score: float = 20.0,
    fallback: bool = False
) -> float:
    """
    Calculate a confidence score (0-1) based on recommendation strength.
    
    Args:
        score: Raw numeric score from the recommender
        num_reasons: Number of matching reasons/features
        max_score: Maximum possible score
        fallback: Whether we're using fallback (non-LLM) explanation
    
    Returns:
        Confidence score between 0 and 1
    """
    # Normalize score to 0-1 range
    score_component = min(score / max_score, 1.0) * 0.6
    
    # Number of reasons component (max 4 reasons => 1.0)
    reason_component = min(num_reasons / 4.0, 1.0) * 0.4
    
    confidence = score_component + reason_component
    
    # Reduce confidence if using fallback (no LLM)
    if fallback:
        confidence *= 0.85
    
    return round(confidence, 2)


def generate_recommendation_explanation(
    user_prefs: Dict,
    song: Dict,
    score: float,
    reasons: list,
    use_llm: bool = True,
    style: str = "neutral"
) -> Tuple[str, float, bool]:
    """
    Generate a natural language explanation for a recommendation using LLM if available.
    
    Args:
        user_prefs: User preference dictionary
        song: Song dictionary with metadata
        score: Numeric score from recommender
        reasons: List of reason strings from scoring
        use_llm: Whether to attempt LLM generation
        style: Explanation style ("neutral", "casual", "technical", "poetic")
    
    Returns:
        Tuple of (explanation_text, confidence_score, used_llm)
    """
    
    # Calculate base confidence
    confidence = _calculate_confidence(score, len(reasons))
    used_llm = False
    
    # Attempt LLM explanation if enabled and API available
    if use_llm and openai is not None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                explanation = _generate_llm_explanation(
                    user_prefs, song, score, reasons, api_key, style
                )
                if explanation:
                    used_llm = True
                    confidence = round(confidence * 1.05, 2)  # Slight boost for LLM explanations
                    return explanation, confidence, used_llm
            except Exception as e:
                logger.warning(f"LLM explanation failed, using fallback: {e}")
    
    # Fallback: Generate explanation from structured reasons
    fallback_explanation = _generate_fallback_explanation(user_prefs, song, reasons)
    confidence = _calculate_confidence(score, len(reasons), fallback=True)
    
    return fallback_explanation, confidence, used_llm


def _generate_llm_explanation(
    user_prefs: Dict,
    song: Dict,
    score: float,
    reasons: list,
    api_key: str,
    style: str = "neutral"
) -> Optional[str]:
    """
    Use OpenAI API to generate a natural language explanation.
    
    Args:
        user_prefs: User preference dictionary
        song: Song dictionary
        score: Numeric score
        reasons: List of reason strings
        api_key: OpenAI API key
        style: Explanation style ("neutral", "casual", "technical", "poetic")
    
    Returns:
        Generated explanation string or None if failed
    """
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Style-specific instructions
        style_instructions = {
            "casual": "Use a friendly, conversational tone. Feel free to use contractions and colloquial language.",
            "technical": "Use precise, analytical language. Focus on the music theory and acoustic properties that match.",
            "poetic": "Use descriptive, evocative language that captures the mood and feeling of the music.",
            "neutral": "Use a clear, professional tone that is easy to understand."
        }
        style_prompt = style_instructions.get(style, style_instructions["neutral"])
        
        prompt = f"""Given a user's music preferences and a song recommendation, generate a 
concise 1-2 sentence explanation of why this song matches their taste.

{style_prompt}

User preferences:
- Favorite genre: {user_prefs.get('genre', 'Unknown')}
- Mood: {user_prefs.get('mood', 'Unknown')}
- Target energy level: {user_prefs.get('energy', 0.5)}
- Likes acoustic: {user_prefs.get('likes_acoustic', False)}

Recommended song:
- Title: {song.get('title', 'Unknown')}
- Artist: {song.get('artist', 'Unknown')}
- Genre: {song.get('genre', 'Unknown')}
- Mood: {song.get('mood', 'Unknown')}
- Energy: {song.get('energy', 0.5)}
- Acousticness: {song.get('acousticness', 0.5)}

Matching reasons: {', '.join(reasons)}

Generate a brief, natural explanation why this song is recommended:"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        
        explanation = response.choices[0].message.content.strip()
        logger.info(f"LLM explanation generated for {song.get('title')}")
        return explanation
        
    except Exception as e:
        logger.error(f"LLM API error: {e}")
        return None


def _generate_fallback_explanation(
    user_prefs: Dict,
    song: Dict,
    reasons: list
) -> str:
    """
    Generate a natural language explanation without LLM (fallback).
    
    Args:
        user_prefs: User preference dictionary
        song: Song dictionary
        reasons: List of reason strings
    
    Returns:
        Generated explanation string
    """
    genre = song.get('genre', 'unknown genre')
    mood = song.get('mood', 'unknown mood')
    title = song.get('title', 'this song')
    artist = song.get('artist', 'unknown artist')
    
    if not reasons:
        return f"{title} by {artist} matches your taste profile."
    
    # Build explanation from reasons
    reason_summary = ", ".join(reasons[:2])  # Take top 2 reasons
    
    explanation = f"{title} by {artist} is a great match because it has {reason_summary}."
    
    return explanation


def log_recommendation_decision(
    session_id: str,
    user_prefs: Dict,
    song: Dict,
    score: float,
    confidence: float,
    explanation: str,
    used_llm: bool,
    log_dir: str = "logs"
) -> None:
    """
    Log recommendation decision to file for auditing and analysis.
    
    Args:
        session_id: Unique session identifier
        user_prefs: User preference dictionary
        song: Song dictionary
        score: Numeric score
        confidence: Confidence score
        explanation: Generated explanation
        used_llm: Whether LLM was used
        log_dir: Directory to write logs
    """
    try:
        os.makedirs(log_dir, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "user_mode": user_prefs.get("mode", "balanced"),
            "user_genre": user_prefs.get("genre"),
            "user_mood": user_prefs.get("mood"),
            "song_title": song.get("title"),
            "song_artist": song.get("artist"),
            "song_genre": song.get("genre"),
            "score": score,
            "confidence": confidence,
            "explanation": explanation,
            "used_llm": used_llm,
        }
        
        log_file = os.path.join(log_dir, f"recommendations_{session_id}.jsonl")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
    except Exception as e:
        logger.error(f"Failed to log recommendation: {e}")
