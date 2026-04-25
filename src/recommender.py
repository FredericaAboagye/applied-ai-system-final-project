from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from collections import Counter
import csv
import logging
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Song:
    """Represents a song and its attributes."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2010
    mood_tag: str = "balanced"
    instrumentalness: float = 0.0
    focus_score: float = 0.5


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    preferred_mood_tag: str = ""
    preferred_decade: int = 2010
    target_popularity: int = 70
    likes_instrumental: bool = False
    target_focus: float = 0.5
    preferred_mode: str = "balanced"


MODE_WEIGHTS = {
    "balanced": {
        "genre": 2.0,
        "mood": 1.5,
        "energy": 1.0,
        "acoustic": 0.5,
        "popularity": 0.4,
        "decade": 0.5,
        "mood_tag": 0.7,
        "instrumentalness": 0.4,
        "focus": 0.6,
    },
    "genre-first": {
        "genre": 2.6,
        "mood": 1.1,
        "energy": 0.9,
        "acoustic": 0.4,
        "popularity": 0.3,
        "decade": 0.5,
        "mood_tag": 0.5,
        "instrumentalness": 0.3,
        "focus": 0.4,
    },
    "mood-first": {
        "genre": 1.2,
        "mood": 2.4,
        "energy": 0.9,
        "acoustic": 0.5,
        "popularity": 0.3,
        "decade": 0.4,
        "mood_tag": 0.9,
        "instrumentalness": 0.4,
        "focus": 0.5,
    },
    "energy-focused": {
        "genre": 1.0,
        "mood": 1.0,
        "energy": 2.0,
        "acoustic": 0.4,
        "popularity": 0.2,
        "decade": 0.3,
        "mood_tag": 0.4,
        "instrumentalness": 0.3,
        "focus": 0.5,
    },
}


NUMERIC_FIELDS = {
    "id": int,
    "energy": float,
    "tempo_bpm": float,
    "valence": float,
    "danceability": float,
    "acousticness": float,
    "popularity": int,
    "release_decade": int,
    "instrumentalness": float,
    "focus_score": float,
}


def _pick_user_value(user_prefs: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Return the first matching user preference from a list of possible keys."""
    for key in keys:
        value = user_prefs.get(key)
        if value is not None:
            return value
    return default


def _similarity(value: float, target: float, max_gap: float) -> float:
    """Convert a distance into a 0-to-1 similarity score."""
    return max(0.0, 1 - abs(float(value) - float(target)) / float(max_gap))


def _estimate_confidence(score: float, num_reasons: int, max_score: float = 20.0) -> float:
    """
    Estimate confidence score (0-1) based on recommendation strength.
    
    Args:
        score: Raw numeric score from the recommender
        num_reasons: Number of matching reasons/features
        max_score: Maximum possible score
    
    Returns:
        Confidence score between 0 and 1
    """
    score_component = min(score / max_score, 1.0) * 0.6
    reason_component = min(num_reasons / 4.0, 1.0) * 0.4
    confidence = score_component + reason_component
    return round(confidence, 2)


def _get_mode_weights(mode: str) -> Dict[str, float]:
    """Return the active weight profile for the chosen scoring mode."""
    return MODE_WEIGHTS.get(mode.lower(), MODE_WEIGHTS["balanced"])


class Recommender:
    """Object-oriented wrapper around the song scoring logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs sorted from highest to lowest score."""
        ranked = recommend_songs(
            {
                "genre": user.favorite_genre,
                "mood": user.favorite_mood,
                "energy": user.target_energy,
                "likes_acoustic": user.likes_acoustic,
                "preferred_mood_tag": user.preferred_mood_tag,
                "preferred_decade": user.preferred_decade,
                "target_popularity": user.target_popularity,
                "likes_instrumental": user.likes_instrumental,
                "target_focus": user.target_focus,
                "mode": user.preferred_mode,
            },
            [song.__dict__ for song in self.songs],
            k=k,
            mode=user.preferred_mode,
        )
        song_lookup = {song.id: song for song in self.songs}
        return [song_lookup[item[0]["id"]] for item in ranked if item[0]["id"] in song_lookup]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a short human-readable explanation for one recommendation."""
        _, reasons = score_song(
            {
                "genre": user.favorite_genre,
                "mood": user.favorite_mood,
                "energy": user.target_energy,
                "likes_acoustic": user.likes_acoustic,
                "preferred_mood_tag": user.preferred_mood_tag,
                "preferred_decade": user.preferred_decade,
                "target_popularity": user.target_popularity,
                "likes_instrumental": user.likes_instrumental,
                "target_focus": user.target_focus,
                "mode": user.preferred_mode,
            },
            song.__dict__,
            mode=user.preferred_mode,
        )
        return "; ".join(reasons) if reasons else "General vibe match."


def load_songs(csv_path: str) -> List[Dict[str, Any]]:
    """Load songs from a CSV file and convert numeric fields."""
    path = Path(csv_path)
    if not path.is_absolute():
        project_root = Path(__file__).resolve().parent.parent
        path = project_root / csv_path

    songs: List[Dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            converted_row: Dict[str, Any] = {}
            for key, value in row.items():
                converter = NUMERIC_FIELDS.get(key)
                converted_row[key] = converter(value) if converter else value
            songs.append(converted_row)
    return songs


def score_song(
    user_prefs: Dict[str, Any], song: Dict[str, Any], mode: str = "balanced"
) -> Tuple[float, List[str]]:
    """Score one song and return both the numeric score and the reasons."""
    active_mode = user_prefs.get("mode", mode)
    weights = _get_mode_weights(active_mode)
    score = 0.0
    reasons: List[str] = []

    preferred_genre = _pick_user_value(user_prefs, "genre", "favorite_genre")
    preferred_mood = _pick_user_value(user_prefs, "mood", "favorite_mood")
    target_energy = _pick_user_value(user_prefs, "energy", "target_energy")
    likes_acoustic = _pick_user_value(user_prefs, "likes_acoustic")
    preferred_mood_tag = _pick_user_value(user_prefs, "preferred_mood_tag")
    preferred_decade = _pick_user_value(user_prefs, "preferred_decade")
    target_popularity = _pick_user_value(user_prefs, "target_popularity")
    likes_instrumental = _pick_user_value(user_prefs, "likes_instrumental")
    target_focus = _pick_user_value(user_prefs, "target_focus")

    if preferred_genre and song.get("genre") == preferred_genre:
        points = weights["genre"]
        score += points
        reasons.append(f"genre match (+{points:.1f})")

    if preferred_mood and song.get("mood") == preferred_mood:
        points = weights["mood"]
        score += points
        reasons.append(f"mood match (+{points:.1f})")

    if target_energy is not None:
        points = _similarity(song.get("energy", 0.0), target_energy, 1.0) * weights["energy"]
        score += points
        reasons.append(f"energy fit (+{points:.2f})")

    if likes_acoustic is not None:
        acousticness = float(song.get("acousticness", 0.0))
        acoustic_match = (likes_acoustic and acousticness >= 0.6) or (
            not likes_acoustic and acousticness <= 0.4
        )
        if acoustic_match:
            points = weights["acoustic"]
            score += points
            reasons.append(f"acoustic fit (+{points:.1f})")

    if preferred_mood_tag and song.get("mood_tag") == preferred_mood_tag:
        points = weights["mood_tag"]
        score += points
        reasons.append(f"detail tag match (+{points:.1f})")

    if target_popularity is not None:
        points = _similarity(song.get("popularity", target_popularity), target_popularity, 100.0) * weights[
            "popularity"
        ]
        score += points
        if points >= 0.15:
            reasons.append(f"popularity fit (+{points:.2f})")

    if preferred_decade is not None:
        points = _similarity(song.get("release_decade", preferred_decade), preferred_decade, 40.0) * weights[
            "decade"
        ]
        score += points
        if points >= 0.15:
            reasons.append(f"era fit (+{points:.2f})")

    if likes_instrumental is not None:
        instrumentalness = float(song.get("instrumentalness", 0.0))
        instrumental_match = (likes_instrumental and instrumentalness >= 0.6) or (
            not likes_instrumental and instrumentalness <= 0.4
        )
        if instrumental_match:
            points = weights["instrumentalness"]
            score += points
            reasons.append(f"instrumental fit (+{points:.1f})")

    if target_focus is not None:
        points = _similarity(song.get("focus_score", target_focus), target_focus, 1.0) * weights["focus"]
        score += points
        if points >= 0.15:
            reasons.append(f"focus fit (+{points:.2f})")

    return score, reasons


def recommend_songs(
    user_prefs: Dict[str, Any], songs: List[Dict[str, Any]], k: int = 5, mode: str = "balanced",
    use_llm: bool = False, session_id: Optional[str] = None
) -> List[Tuple[Dict[str, Any], float, str, float, bool]]:
    """
    Score songs, rerank with a diversity penalty, and return the top-k results.
    
    Args:
        user_prefs: User preferences dictionary
        songs: List of song dictionaries
        k: Number of recommendations to return
        mode: Scoring mode (balanced, genre-first, mood-first, energy-focused)
        use_llm: Whether to generate LLM-based explanations
        session_id: Unique session identifier for logging
    
    Returns:
        List of tuples: (song_dict, score, explanation, confidence, used_llm)
    """
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    # Import LLM explainer here to avoid hard dependency on OpenAI
    try:
        from .llm_explainer import generate_recommendation_explanation, log_recommendation_decision
    except ImportError:
        generate_recommendation_explanation = None
        log_recommendation_decision = None
    
    active_mode = user_prefs.get("mode", mode)
    scored_candidates = []

    for song in songs:
        score, reasons = score_song(user_prefs, song, mode=active_mode)
        scored_candidates.append({"song": song, "score": score, "reasons": reasons})

    selected: List[Tuple[Dict[str, Any], float, str, float, bool]] = []
    remaining = scored_candidates.copy()
    artist_counts: Counter[str] = Counter()
    genre_counts: Counter[str] = Counter()

    while remaining and len(selected) < k:
        best_index = 0
        best_adjusted_score = float("-inf")
        best_penalties: List[str] = []

        for index, candidate in enumerate(remaining):
            adjusted_score = candidate["score"]
            penalties: List[str] = []
            artist = str(candidate["song"].get("artist", ""))
            genre = str(candidate["song"].get("genre", ""))

            if artist_counts[artist] > 0:
                penalty = 0.35 * artist_counts[artist]
                adjusted_score -= penalty
                penalties.append(f"diversity penalty (-{penalty:.2f} same artist)")

            if genre_counts[genre] > 0:
                penalty = 0.15 * genre_counts[genre]
                adjusted_score -= penalty
                penalties.append(f"diversity penalty (-{penalty:.2f} same genre)")

            if adjusted_score > best_adjusted_score:
                best_index = index
                best_adjusted_score = adjusted_score
                best_penalties = penalties

        chosen = remaining.pop(best_index)
        chosen_song = chosen["song"]
        artist_counts[str(chosen_song.get("artist", ""))] += 1
        genre_counts[str(chosen_song.get("genre", ""))] += 1

        explanation_parts = chosen["reasons"] + best_penalties
        base_explanation = "; ".join(explanation_parts) if explanation_parts else f"{active_mode} mode match"
        
        # Generate LLM-based explanation if available
        confidence = 0.0
        used_llm = False
        if use_llm and generate_recommendation_explanation:
            try:
                explanation, confidence, used_llm = generate_recommendation_explanation(
                    user_prefs, chosen_song, round(best_adjusted_score, 2), chosen["reasons"], use_llm=True
                )
                # Log the decision
                if log_recommendation_decision:
                    log_recommendation_decision(
                        session_id, user_prefs, chosen_song, round(best_adjusted_score, 2),
                        confidence, explanation, used_llm
                    )
            except Exception as e:
                logger.warning(f"Failed to generate LLM explanation: {e}")
                explanation = base_explanation
                confidence = _estimate_confidence(round(best_adjusted_score, 2), len(chosen["reasons"]))
        else:
            explanation = base_explanation
            confidence = _estimate_confidence(round(best_adjusted_score, 2), len(chosen["reasons"]))
        
        selected.append((chosen_song, round(best_adjusted_score, 2), explanation, confidence, used_llm))

    return selected

