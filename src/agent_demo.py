"""
Stretch features demonstration for VibeFinder 2.0.

Demonstrates all three stretch features in sequence:
  1. RAG - multi-source retrieval from two song catalogs
  2. Agentic workflow - multi-step planning with observable reasoning
  3. Persona specialization - few-shot weight tuning with before/after comparison

Run with: python -m src.agent_demo
"""

import os
from tabulate import tabulate
from src.retriever import retrieve_from_sources
from src.agent import run_agent
from src.persona import detect_persona, get_persona_weights, PERSONAS
from src.recommender import recommend_songs, SCORING_MODES

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_1 = os.path.join(BASE_DIR, "data", "songs.csv")
SOURCE_2 = os.path.join(BASE_DIR, "data", "extended_songs.csv")


def demo_rag() -> None:
    """
    Show that multi-source retrieval improves results for niche genre users.
    Compares jazz recommendations from Source 1 alone vs Source 1 + Source 2.
    """
    print("\n" + "=" * 60)
    print("  STRETCH 1: RAG - Multi-Source Retrieval")
    print("=" * 60)

    jazz_prefs = {
        "genre": "jazz", "mood": "relaxed", "energy": 0.45, "likes_acoustic": False,
    }

    print("\n  Source 1 only (original 18-song catalog):")
    songs_single = retrieve_from_sources([SOURCE_1])
    recs_single = recommend_songs(jazz_prefs, songs_single, k=5)
    jazz_hits_single = sum(1 for r in recs_single if r[0]["genre"] == "jazz")
    print(f"  Jazz songs in top 5: {jazz_hits_single}/5")
    for i, (song, score, _) in enumerate(recs_single, 1):
        print(f"    #{i} {song['title']} ({song['genre']}, score={score:.2f})")

    print("\n  Source 1 + Source 2 (extended catalog, 28 songs):")
    songs_multi = retrieve_from_sources([SOURCE_1, SOURCE_2])
    recs_multi = recommend_songs(jazz_prefs, songs_multi, k=5)
    jazz_hits_multi = sum(1 for r in recs_multi if r[0]["genre"] == "jazz")
    print(f"  Jazz songs in top 5: {jazz_hits_multi}/5")
    for i, (song, score, _) in enumerate(recs_multi, 1):
        print(f"    #{i} {song['title']} ({song['genre']}, score={score:.2f})")

    print(f"\n  Impact: {jazz_hits_single} jazz match(es) -> {jazz_hits_multi} jazz match(es) "
          f"(+{jazz_hits_multi - jazz_hits_single} from extended catalog)")


def demo_agent() -> None:
    """
    Run the multi-step recommendation agent on two profiles.
    All intermediate reasoning steps are printed to the terminal.
    """
    print("\n" + "=" * 60)
    print("  STRETCH 2: Agentic Workflow")
    print("=" * 60)

    songs = retrieve_from_sources([SOURCE_1, SOURCE_2])

    blues_prefs = {
        "genre": "blues", "mood": "moody", "energy": 0.45,
        "likes_acoustic": True, "preferred_decade": "2010s",
    }
    run_agent(blues_prefs, songs, "Blues/Moody (niche genre - agent should adapt)")

    conflict_prefs = {
        "genre": "ambient", "mood": "hype", "energy": 0.92,
        "likes_acoustic": False,
    }
    run_agent(conflict_prefs, songs, "Ambient + Hype (conflicting prefs - agent should resolve)")


def demo_persona() -> None:
    """
    Detect the closest persona for two user profiles and apply specialized weights.
    Shows side-by-side comparison of baseline vs persona-specialized results.
    """
    print("\n" + "=" * 60)
    print("  STRETCH 3: Fine-Tuning via Persona Specialization")
    print("=" * 60)

    songs = retrieve_from_sources([SOURCE_1, SOURCE_2])

    test_profiles = [
        {
            "genre": "pop", "mood": "moody", "energy": 0.6,
            "likes_acoustic": False,
        },
        {
            "genre": "pop", "mood": "happy", "energy": 0.4,
            "likes_acoustic": True,
        },
    ]

    for prefs in test_profiles:
        persona_name, similarity = detect_persona(prefs)
        persona_weights = get_persona_weights(persona_name)

        print(f"\n  Profile: genre={prefs['genre']}, mood={prefs['mood']}, energy={prefs['energy']}")
        print(f"  Detected persona : {persona_name} (similarity={similarity:.2f})")
        print(f"  Description      : {PERSONAS[persona_name]['description']}")

        baseline_recs = recommend_songs(prefs, songs, k=3, mode="genre-first", diversity=False)

        SCORING_MODES["_persona_temp"] = persona_weights
        persona_recs = recommend_songs(prefs, songs, k=3, mode="_persona_temp", diversity=False)
        del SCORING_MODES["_persona_temp"]

        rows = []
        for i, ((bs, bscore, _), (ps, pscore, _)) in enumerate(
            zip(baseline_recs, persona_recs), 1
        ):
            marker = "<-- changed" if bs["title"] != ps["title"] else ""
            rows.append([
                f"#{i}",
                bs["title"], f"{bscore:.2f}",
                ps["title"], f"{pscore:.2f}",
                marker,
            ])

        headers = ["#", "Baseline Title", "B.Score", "Persona Title", "P.Score", ""]
        print()
        print(tabulate(rows, headers=headers, tablefmt="simple"))

        changed = sum(1 for b, p in zip(baseline_recs, persona_recs)
                      if b[0]["title"] != p[0]["title"])
        print(f"  {changed}/3 positions differ from baseline.")


def main() -> None:
    demo_rag()
    demo_agent()
    demo_persona()


if __name__ == "__main__":
    main()
