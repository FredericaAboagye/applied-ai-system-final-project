"""Command-line runner for the Music Recommender Simulation."""

import logging
from textwrap import shorten
from pathlib import Path
from dotenv import load_dotenv

try:
    from .recommender import load_songs, recommend_songs
    from .llm_explainer import log_recommendation_decision
except ImportError:
    from recommender import load_songs, recommend_songs
    from llm_explainer import log_recommendation_decision

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _print_table(headers: list, rows: list) -> None:
    """Print a simple ASCII table for the recommendations."""
    widths = [4, 22, 18, 8, 8, 50]

    def format_row(values: list) -> str:
        cleaned = [
            str(values[0]).ljust(widths[0]),
            shorten(str(values[1]), width=widths[1], placeholder="...").ljust(widths[1]),
            shorten(str(values[2]), width=widths[2], placeholder="...").ljust(widths[2]),
            str(values[3]).rjust(widths[3]),
            str(values[4]).rjust(widths[4]) if len(values) > 4 else "",
            shorten(str(values[5] if len(values) > 5 else ""), width=widths[5], placeholder="...").ljust(widths[5]) if len(values) > 5 else "",
        ]
        return "| " + " | ".join(cleaned) + " |"

    border = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    print(border)
    print(format_row(headers))
    print(border)
    for row in rows:
        print(format_row(row))
    print(border)


def print_profile_recommendations(profile_name: str, user_prefs: dict, songs: list, mode: str, use_llm: bool = False, style: str = "neutral") -> None:
    """Print the top recommendations for one evaluation profile."""
    print(f"\n{'=' * 120}")
    print(f"{profile_name}  |  mode={mode}" + (f" (LLM explanations: {'ON' if use_llm else 'OFF'})" if use_llm is not None else ""))
    if style != "neutral":
        print(f"Explanation style: {style}")
    print(
        "Preferences: "
        f"genre={user_prefs['genre']}, mood={user_prefs['mood']}, energy={user_prefs['energy']}, "
        f"tag={user_prefs['preferred_mood_tag']}, decade={user_prefs['preferred_decade']}, "
        f"focus={user_prefs['target_focus']}"
    )

    recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode, use_llm=use_llm, style=style)
    rows = []
    for index, rec in enumerate(recommendations, start=1):
        song, score, explanation, confidence, used_llm = rec
        llm_indicator = " [LLM]" if used_llm else ""
        rows.append([
            index, 
            song['title'], 
            song['artist'], 
            f"{score:.2f}", 
            f"{confidence:.2f}",
            explanation
        ])
    _print_table(["#", "Title", "Artist", "Score", "Conf", "Explanation"], rows)


def main() -> None:
    """Load songs and evaluate the recommender with multiple profiles and modes."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print("Scoring modes: balanced, genre-first, mood-first, energy-focused")
    print("Features: confidence scoring, explanation generation, diversity reranking\n")

    evaluation_profiles = [
        (
            "High-Energy Pop",
            {
                "genre": "pop",
                "mood": "happy",
                "energy": 0.90,
                "likes_acoustic": False,
                "preferred_mood_tag": "bright",
                "preferred_decade": 2020,
                "target_popularity": 85,
                "likes_instrumental": False,
                "target_focus": 0.40,
            },
            "genre-first",
        ),
        (
            "Chill Lofi",
            {
                "genre": "lofi",
                "mood": "chill",
                "energy": 0.35,
                "likes_acoustic": True,
                "preferred_mood_tag": "cozy",
                "preferred_decade": 2010,
                "target_popularity": 75,
                "likes_instrumental": True,
                "target_focus": 0.95,
            },
            "mood-first",
        ),
        (
            "Deep Intense Rock",
            {
                "genre": "rock",
                "mood": "intense",
                "energy": 0.95,
                "likes_acoustic": False,
                "preferred_mood_tag": "driving",
                "preferred_decade": 2010,
                "target_popularity": 80,
                "likes_instrumental": False,
                "target_focus": 0.30,
            },
            "energy-focused",
        ),
        (
            "Edge Case: Acoustic but Intense",
            {
                "genre": "ambient",
                "mood": "intense",
                "energy": 0.90,
                "likes_acoustic": True,
                "preferred_mood_tag": "cinematic",
                "preferred_decade": 2020,
                "target_popularity": 65,
                "likes_instrumental": True,
                "target_focus": 0.85,
            },
            "balanced",
        ),
    ]

    for profile_name, user_prefs, mode in evaluation_profiles:
        print_profile_recommendations(profile_name, user_prefs, songs, mode)

    # BONUS: Demonstrate explanation style specialization (Fine-Tuning Feature)
    print(f"\n\n{'='*120}")
    print("BONUS FEATURE: Explanation Style Specialization (Fine-Tuning)")
    print(f"{'='*120}")
    print("Demonstrating how the same recommendation can be explained in different styles:\n")
    
    demo_profile = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.90,
        "likes_acoustic": False,
        "preferred_mood_tag": "bright",
        "preferred_decade": 2020,
        "target_popularity": 85,
        "likes_instrumental": False,
        "target_focus": 0.40,
    }
    
    styles = ["neutral", "casual", "technical", "poetic"]
    print(f"User Profile: Pop fan, happy mood, high energy\n")
    
    for style in styles:
        print(f"\n--- Style: {style.upper()} ---")
        recommendations = recommend_songs(demo_profile, songs, k=1, mode="genre-first", use_llm=True, style=style)
        if recommendations:
            song, score, explanation, confidence, used_llm = recommendations[0]
            print(f"Song: {song['title']} by {song['artist']}")
            print(f"Explanation ({style}): {explanation}")
            print(f"Confidence: {confidence:.2f}")


if __name__ == "__main__":
    main()
