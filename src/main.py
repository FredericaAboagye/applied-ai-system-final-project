"""Command-line runner for the Music Recommender Simulation."""

try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


def print_profile_recommendations(profile_name: str, user_prefs: dict, songs: list) -> None:
    """Print the top recommendations for one evaluation profile."""
    print(f"\n{'=' * 72}")
    print(profile_name)
    print(
        "Preferences: "
        f"genre={user_prefs['genre']}, "
        f"mood={user_prefs['mood']}, "
        f"energy={user_prefs['energy']}, "
        f"likes_acoustic={user_prefs['likes_acoustic']}"
    )
    print("-" * 72)

    recommendations = recommend_songs(user_prefs, songs, k=5)
    for index, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{index}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f}")
        print(f"   Why: {explanation}")
        print()


def main() -> None:
    """Load songs and evaluate the recommender with multiple user profiles."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    evaluation_profiles = {
        "High-Energy Pop": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.90,
            "likes_acoustic": False,
        },
        "Chill Lofi": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.35,
            "likes_acoustic": True,
        },
        "Deep Intense Rock": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.95,
            "likes_acoustic": False,
        },
        "Edge Case: Acoustic but Intense": {
            "genre": "ambient",
            "mood": "intense",
            "energy": 0.90,
            "likes_acoustic": True,
        },
    }

    for profile_name, user_prefs in evaluation_profiles.items():
        print_profile_recommendations(profile_name, user_prefs, songs)


if __name__ == "__main__":
    main()
