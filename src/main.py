"""Command-line runner for the Music Recommender Simulation."""

from textwrap import shorten

try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


def _print_table(headers: list, rows: list) -> None:
    """Print a simple ASCII table for the recommendations."""
    widths = [4, 22, 18, 8, 74]

    def format_row(values: list) -> str:
        cleaned = [
            str(values[0]).ljust(widths[0]),
            shorten(str(values[1]), width=widths[1], placeholder="...").ljust(widths[1]),
            shorten(str(values[2]), width=widths[2], placeholder="...").ljust(widths[2]),
            str(values[3]).rjust(widths[3]),
            shorten(str(values[4]), width=widths[4], placeholder="...").ljust(widths[4]),
        ]
        return "| " + " | ".join(cleaned) + " |"

    border = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    print(border)
    print(format_row(headers))
    print(border)
    for row in rows:
        print(format_row(row))
    print(border)


def print_profile_recommendations(profile_name: str, user_prefs: dict, songs: list, mode: str) -> None:
    """Print the top recommendations for one evaluation profile."""
    print(f"\n{'=' * 120}")
    print(f"{profile_name}  |  mode={mode}")
    print(
        "Preferences: "
        f"genre={user_prefs['genre']}, mood={user_prefs['mood']}, energy={user_prefs['energy']}, "
        f"tag={user_prefs['preferred_mood_tag']}, decade={user_prefs['preferred_decade']}, "
        f"focus={user_prefs['target_focus']}"
    )

    recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode)
    rows = []
    for index, (song, score, explanation) in enumerate(recommendations, start=1):
        rows.append([index, song['title'], song['artist'], f"{score:.2f}", explanation])
    _print_table(["#", "Title", "Artist", "Score", "Reasons"], rows)


def main() -> None:
    """Load songs and evaluate the recommender with multiple profiles and modes."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print("Scoring modes: balanced, genre-first, mood-first, energy-focused")

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


if __name__ == "__main__":
    main()
