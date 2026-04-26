"""
Command line runner for VibeFinder - Music Recommender Simulation.
Run with: python -m src.main
"""

import os
from tabulate import tabulate
from src.recommender import recommend_songs, SCORING_MODES
from src.guardrails import validate_user_prefs, check_output_confidence
from src.retriever import retrieve_from_sources


PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
        "likes_acoustic": False,
        "detailed_mood": "euphoric",
        "preferred_decade": "2020s",
        "avoid_explicit": False,
        "prefers_instrumental": False,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "likes_acoustic": True,
        "detailed_mood": "mellow",
        "preferred_decade": "2020s",
        "avoid_explicit": False,
        "prefers_instrumental": True,
    },
    "Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.95,
        "likes_acoustic": False,
        "detailed_mood": "aggressive",
        "preferred_decade": "2010s",
        "avoid_explicit": False,
        "prefers_instrumental": False,
    },
    "Edge Case - Conflicting Prefs": {
        "genre": "ambient",
        "mood": "hype",
        "energy": 0.92,
        "likes_acoustic": True,
        "detailed_mood": "euphoric",
        "preferred_decade": "2020s",
        "avoid_explicit": True,
        "prefers_instrumental": False,
    },
}


def print_profile_results(name: str, prefs: dict, songs: list, mode: str) -> None:
    separator = "=" * 70
    print(f"\n{separator}")
    print(f"  Profile : {name}")
    print(f"  Mode    : {mode}")
    print(separator)
    print(f"  genre={prefs['genre']}  mood={prefs['mood']}  energy={prefs['energy']}")
    print(
        f"  detailed_mood={prefs.get('detailed_mood', '')}  "
        f"decade={prefs.get('preferred_decade', '')}  "
        f"avoid_explicit={prefs.get('avoid_explicit', False)}"
    )
    print(f"{separator}\n")

    # Guardrail: validate inputs before scoring
    errors = validate_user_prefs(prefs)
    if errors:
        for err in errors:
            print(f"  [GUARDRAIL] Input warning: {err}")

    recommendations = recommend_songs(prefs, songs, k=5, mode=mode, diversity=True)

    # Guardrail: check output confidence
    warning = check_output_confidence(recommendations)
    if warning:
        print(f"  [GUARDRAIL] {warning}\n")

    table_rows = []
    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        table_rows.append([
            f"#{i}",
            song["title"],
            song["artist"],
            song["genre"],
            song["mood"],
            song["energy"],
            song["popularity"],
            f"{score:.2f}",
            explanation,
        ])

    headers = ["#", "Title", "Artist", "Genre", "Mood", "Energy", "Pop", "Score", "Why"]
    print(tabulate(
        table_rows, headers=headers, tablefmt="simple",
        maxcolwidths=[3, 22, 16, 10, 8, 6, 4, 6, 55],
    ))
    print()


def main() -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_1 = os.path.join(base_dir, "data", "songs.csv")
    source_2 = os.path.join(base_dir, "data", "extended_songs.csv")

    songs = retrieve_from_sources([source_1, source_2])

    for name, prefs in PROFILES.items():
        for mode in SCORING_MODES:
            print_profile_results(name, prefs, songs, mode)


if __name__ == "__main__":
    main()
