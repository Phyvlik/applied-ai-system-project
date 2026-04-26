from typing import List, Optional

VALID_GENRES = {
    "pop", "lofi", "rock", "ambient", "jazz", "synthwave",
    "indie pop", "country", "hip-hop", "classical", "metal",
    "reggae", "blues", "edm", "folk",
}

VALID_MOODS = {"happy", "chill", "intense", "relaxed", "moody", "focused", "hype"}

LOW_CONFIDENCE_THRESHOLD = 3.0


def validate_user_prefs(prefs: dict) -> List[str]:
    """Return a list of validation error strings. Empty list means valid."""
    errors = []

    genre = prefs.get("genre", "").strip().lower()
    if genre and genre not in VALID_GENRES:
        errors.append(
            f"Unknown genre '{genre}'. Known genres: {', '.join(sorted(VALID_GENRES))}"
        )

    mood = prefs.get("mood", "").strip().lower()
    if mood and mood not in VALID_MOODS:
        errors.append(
            f"Unknown mood '{mood}'. Known moods: {', '.join(sorted(VALID_MOODS))}"
        )

    energy = prefs.get("energy")
    if energy is not None and not (0.0 <= float(energy) <= 1.0):
        errors.append(f"Energy must be between 0.0 and 1.0, got {energy}")

    return errors


def check_output_confidence(recommendations: list) -> Optional[str]:
    """Return a warning string if the top recommendation score is below the threshold."""
    if not recommendations:
        return "No recommendations generated."
    top_score = recommendations[0][1]
    if top_score < LOW_CONFIDENCE_THRESHOLD:
        return (
            f"Low confidence: top score is {top_score:.2f} "
            f"(threshold {LOW_CONFIDENCE_THRESHOLD}). "
            "Preferences may not match the catalog well."
        )
    return None
