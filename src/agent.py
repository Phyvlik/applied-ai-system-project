"""
Multi-step recommendation agent for VibeFinder.

Each step prints its reasoning so intermediate decisions are fully
observable. The agent analyzes the user profile, selects the best
scoring strategy, runs recommendations, evaluates quality, and adapts
if the initial results are low confidence.
"""

from src.recommender import recommend_songs
from src.guardrails import validate_user_prefs, check_output_confidence

LOW_GENRE_COVERAGE = 2


def _count_genre(songs: list, genre: str) -> int:
    return sum(1 for s in songs if s.get("genre", "").lower() == genre.lower())


def _analyze_profile(user_prefs: dict, songs: list) -> dict:
    print("\n  [AGENT] Step 1: Analyzing profile...")
    genre = user_prefs.get("genre", "")
    mood = user_prefs.get("mood", "")
    energy = float(user_prefs.get("energy", 0.5))
    genre_count = _count_genre(songs, genre)

    issues = []
    if genre_count < LOW_GENRE_COVERAGE:
        issues.append(f"low genre coverage ({genre_count} song(s) for '{genre}')")
    if energy > 0.85 and mood in ("chill", "relaxed"):
        issues.append("conflicting signals: high energy with calm mood")

    print(f"  genre='{genre}' ({genre_count} songs in catalog)  mood='{mood}'  energy={energy}")
    if issues:
        for issue in issues:
            print(f"  [!] {issue}")
    else:
        print("  No conflicts detected.")

    return {"genre_count": genre_count, "issues": issues}


def _select_strategy(analysis: dict) -> dict:
    print("\n  [AGENT] Step 2: Selecting strategy...")
    issues = analysis.get("issues", [])
    genre_count = analysis.get("genre_count", 10)

    if genre_count < LOW_GENRE_COVERAGE:
        mode = "mood-first"
        reason = "genre coverage too low, switching to mood-first"
    elif any("conflicting" in i for i in issues):
        mode = "energy-focused"
        reason = "conflicting energy/mood detected, switching to energy-focused"
    else:
        mode = "genre-first"
        reason = "profile is clean, using genre-first"

    print(f"  Mode selected: {mode}  |  Reason: {reason}")
    return {"mode": mode, "reason": reason}


def _evaluate_results(recommendations: list) -> dict:
    print("\n  [AGENT] Step 4: Evaluating results...")
    if not recommendations:
        print("  No results returned.")
        return {"quality": "empty", "top_score": 0}

    top_score = recommendations[0][1]
    genre_diversity = len({r[0]["genre"] for r in recommendations})

    print(f"  Top score: {top_score:.2f}  |  Genre diversity: {genre_diversity} genres in top 5")

    if top_score < 3.0:
        quality = "low"
        print("  Verdict: low confidence, attempting to adapt.")
    elif top_score < 5.0:
        quality = "medium"
        print("  Verdict: moderate confidence, results accepted.")
    else:
        quality = "high"
        print("  Verdict: high confidence, results accepted.")

    return {"quality": quality, "top_score": top_score}


def run_agent(user_prefs: dict, songs: list, profile_name: str = "Profile") -> list:
    """
    Run the full multi-step recommendation agent and return final results.
    All intermediate reasoning steps are printed to the terminal.
    """
    separator = "-" * 55
    print(f"\n{separator}")
    print(f"  AGENT RUN: {profile_name}")
    print(separator)

    # Step 1: Analyze profile
    analysis = _analyze_profile(user_prefs, songs)

    # Step 2: Select strategy
    strategy = _select_strategy(analysis)
    mode = strategy["mode"]

    # Step 3: Run recommendations
    print(f"\n  [AGENT] Step 3: Running recommendations (mode={mode})...")
    errors = validate_user_prefs(user_prefs)
    for err in errors:
        print(f"  [GUARDRAIL] {err}")

    recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode, diversity=True)
    print(f"  Generated {len(recommendations)} recommendations.")

    # Step 4: Evaluate quality
    evaluation = _evaluate_results(recommendations)

    # Step 5: Adapt if low confidence
    if evaluation["quality"] == "low":
        print("\n  [AGENT] Step 5: Adapting strategy (low confidence)...")
        fallback_mode = "energy-focused"
        retry_recs = recommend_songs(user_prefs, songs, k=5, mode=fallback_mode, diversity=True)
        new_top = retry_recs[0][1] if retry_recs else 0
        print(f"  Retry with '{fallback_mode}': top score {new_top:.2f}")
        if new_top > evaluation["top_score"]:
            print(f"  Improvement found, using {fallback_mode} results.")
            recommendations = retry_recs
        else:
            print("  No improvement found, keeping original results.")
    else:
        print("\n  [AGENT] Step 5: No adaptation needed.")

    # Final confidence check
    warning = check_output_confidence(recommendations)
    if warning:
        print(f"\n  [GUARDRAIL] {warning}")

    print(f"{separator}")
    return recommendations
