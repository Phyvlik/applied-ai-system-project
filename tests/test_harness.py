"""
Evaluation harness for VibeFinder.

Runs predefined test cases against the recommender and prints a pass/fail summary.
Run with: python -m tests.test_harness
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommender import load_songs, recommend_songs
from src.guardrails import validate_user_prefs, check_output_confidence, LOW_CONFIDENCE_THRESHOLD

TEST_CASES = [
    {
        "name": "Pop/Happy - top result should be pop genre",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
        "check": lambda recs: recs[0][0]["genre"] == "pop",
    },
    {
        "name": "Lofi/Chill - top result should be lofi genre",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": True},
        "check": lambda recs: recs[0][0]["genre"] == "lofi",
    },
    {
        "name": "Rock/Intense - top result should be rock genre",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
        "check": lambda recs: recs[0][0]["genre"] == "rock",
    },
    {
        "name": "EDM/Hype - top result should be edm genre",
        "prefs": {"genre": "edm", "mood": "hype", "energy": 0.95, "likes_acoustic": False},
        "check": lambda recs: recs[0][0]["genre"] == "edm",
    },
    {
        "name": "Unknown genre - guardrail should flag input error",
        "prefs": {"genre": "polka", "mood": "happy", "energy": 0.5, "likes_acoustic": False},
        "check": lambda recs: len(validate_user_prefs(
            {"genre": "polka", "mood": "happy", "energy": 0.5}
        )) > 0,
    },
    {
        "name": "Energy out of range - guardrail should flag input error",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 1.8, "likes_acoustic": False},
        "check": lambda recs: len(validate_user_prefs(
            {"genre": "pop", "mood": "happy", "energy": 1.8}
        )) > 0,
    },
    {
        "name": "Valid prefs - at least 5 results returned",
        "prefs": {"genre": "jazz", "mood": "relaxed", "energy": 0.4, "likes_acoustic": False},
        "check": lambda recs: len(recs) == 5,
    },
    {
        "name": "Diversity - top 5 should not repeat the same artist twice",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
        "check": lambda recs: len({r[0]["artist"] for r in recs}) == len(recs),
    },
]


def run_harness() -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "songs.csv")
    songs = load_songs(csv_path)

    passed = 0
    failed = 0

    print("=" * 60)
    print("VibeFinder Evaluation Harness")
    print("=" * 60)

    for tc in TEST_CASES:
        try:
            recs = recommend_songs(tc["prefs"], songs, k=5)
            result = tc["check"](recs)
        except Exception as e:
            result = False
            print(f"[ERROR] {tc['name']}: {e}")

        status = "PASS" if result else "FAIL"
        if result:
            passed += 1
        else:
            failed += 1

        top = recs[0] if recs else ({"title": "N/A", "genre": "N/A"}, 0, "")
        print(
            f"[{status}] {tc['name']}\n"
            f"       Top: {top[0]['title']} | genre={top[0]['genre']} | score={top[1]:.2f}\n"
        )

    total = passed + failed
    pct = int(100 * passed / total) if total else 0
    print("=" * 60)
    print(f"Results: {passed}/{total} passed ({pct}% pass rate)")
    print("=" * 60)


if __name__ == "__main__":
    run_harness()
