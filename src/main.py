"""
Command line runner for the Music Recommender Simulation.
Run with: python -m src.main
"""

import os
from src.recommender import load_songs, recommend_songs


PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "likes_acoustic": True,
    },
    "Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.95,
        "likes_acoustic": False,
    },
    "Edge Case — Conflicting Prefs (ambient + hype + high energy)": {
        "genre": "ambient",
        "mood": "hype",
        "energy": 0.92,
        "likes_acoustic": True,
    },
}


def print_profile_results(name: str, prefs: dict, songs: list) -> None:
    separator = "=" * 60
    print(f"\n{separator}")
    print(f"  Profile: {name}")
    print(separator)
    print(f"  genre={prefs['genre']}  mood={prefs['mood']}  "
          f"energy={prefs['energy']}  likes_acoustic={prefs['likes_acoustic']}")
    print(f"{separator}\n")

    recommendations = recommend_songs(prefs, songs, k=5)
    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  #{i}  {song['title']} by {song['artist']}")
        print(f"       Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']}")
        print(f"       Score: {score:.2f}")
        print(f"       Why:   {explanation}")
        print()


def main() -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "songs.csv")

    songs = load_songs(csv_path)

    for name, prefs in PROFILES.items():
        print_profile_results(name, prefs, songs)


if __name__ == "__main__":
    main()
