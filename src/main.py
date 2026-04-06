"""Command-line runner for the Music Recommender Simulation."""

try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


def main() -> None:
    """Load songs, compute recommendations, and print them clearly."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for index, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{index}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f}")
        print(f"   Why: {explanation}")
        print()


if __name__ == "__main__":
    main()
