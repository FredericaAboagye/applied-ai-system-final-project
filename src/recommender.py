from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import csv


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


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """Object-oriented wrapper around the song scoring logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs sorted from highest to lowest score."""
        scored_songs = sorted(
            self.songs,
            key=lambda song: score_song(
                {
                    "genre": user.favorite_genre,
                    "mood": user.favorite_mood,
                    "energy": user.target_energy,
                    "likes_acoustic": user.likes_acoustic,
                },
                song.__dict__,
            )[0],
            reverse=True,
        )
        return scored_songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a short human-readable explanation for one recommendation."""
        _, reasons = score_song(
            {
                "genre": user.favorite_genre,
                "mood": user.favorite_mood,
                "energy": user.target_energy,
                "likes_acoustic": user.likes_acoustic,
            },
            song.__dict__,
        )
        return "; ".join(reasons) if reasons else "General vibe match."


NUMERIC_FIELDS = {
    "id": int,
    "energy": float,
    "tempo_bpm": float,
    "valence": float,
    "danceability": float,
    "acousticness": float,
}


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


def score_song(user_prefs: Dict[str, Any], song: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score one song and return both the numeric score and the reasons."""
    score = 0.0
    reasons: List[str] = []

    preferred_genre = user_prefs.get("genre") or user_prefs.get("favorite_genre")
    preferred_mood = user_prefs.get("mood") or user_prefs.get("favorite_mood")
    target_energy = user_prefs.get("energy")
    if target_energy is None:
        target_energy = user_prefs.get("target_energy")
    likes_acoustic = user_prefs.get("likes_acoustic")

    if preferred_genre and song.get("genre") == preferred_genre:
        score += 2.0
        reasons.append("genre match (+2.0)")

    if preferred_mood and song.get("mood") == preferred_mood:
        score += 1.5
        reasons.append("mood match (+1.5)")

    if target_energy is not None:
        energy_similarity = max(0.0, 1 - abs(float(song.get("energy", 0.0)) - float(target_energy)))
        score += energy_similarity
        reasons.append(f"energy similarity (+{energy_similarity:.2f})")

    if likes_acoustic is not None:
        acousticness = float(song.get("acousticness", 0.0))
        acoustic_match = (likes_acoustic and acousticness >= 0.6) or (
            not likes_acoustic and acousticness <= 0.4
        )
        if acoustic_match:
            score += 0.5
            reasons.append("acoustic preference match (+0.5)")

    return score, reasons


def recommend_songs(
    user_prefs: Dict[str, Any], songs: List[Dict[str, Any]], k: int = 5
) -> List[Tuple[Dict[str, Any], float, str]]:
    """Score every song, rank the catalog, and return the top-k results."""
    scored_results: List[Tuple[Dict[str, Any], float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "General vibe match."
        scored_results.append((song, score, explanation))

    ranked_results = sorted(scored_results, key=lambda item: item[1], reverse=True)
    return ranked_results[:k]

