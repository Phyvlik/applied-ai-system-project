"""
Command line runner for the Music Recommender Simulation.
Run with: python -m src.main
"""

import os
from src.recommender import load_songs, recommend_songs


def main() -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "songs.csv")

    songs = load_songs(csv_path)

    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    }

    print("\n--- User Profile ---")
    for key, val in user_prefs.items():
        print(f"  {key}: {val}")

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n--- Top Recommendations ---\n")
    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"#{i}  {song['title']} by {song['artist']}")
        print(f"    Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']}")
        print(f"    Score: {score:.2f}")
        print(f"    Why:   {explanation}")
        print()


if __name__ == "__main__":
    main()
