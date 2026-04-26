"""
Few-shot persona detection and specialized weight profiles for VibeFinder.

Five reference personas are defined as named example user profiles.
Given a new user's preferences, the system finds the closest matching
persona and applies its specialized scoring weights. Output is then
compared to the baseline genre-first result to show measurable difference.
"""

from typing import Dict, Tuple

PERSONAS: Dict[str, dict] = {
    "Gym Warrior": {
        "example": {
            "genre": "edm", "mood": "hype", "energy": 0.95, "likes_acoustic": False,
        },
        "description": "High-intensity workout listener, wants maximum energy and drive",
        "weights": {
            "genre": 1.5, "mood": 2.0, "energy": 3.5, "valence": 0.5,
            "acoustic": 0.0, "popularity": 0.5, "decade": 0.2, "detailed_mood": 1.0,
        },
    },
    "Study Focus": {
        "example": {
            "genre": "lofi", "mood": "focused", "energy": 0.35, "likes_acoustic": True,
        },
        "description": "Background music for deep work, prefers calm and instrumental",
        "weights": {
            "genre": 1.5, "mood": 2.5, "energy": 2.5, "valence": 1.0,
            "acoustic": 1.5, "popularity": 0.1, "decade": 0.2, "detailed_mood": 1.5,
        },
    },
    "Late Night Drive": {
        "example": {
            "genre": "synthwave", "mood": "moody", "energy": 0.70, "likes_acoustic": False,
        },
        "description": "Atmospheric late-night listening, moody and cinematic",
        "weights": {
            "genre": 2.0, "mood": 3.0, "energy": 1.5, "valence": 1.5,
            "acoustic": 0.3, "popularity": 0.2, "decade": 0.5, "detailed_mood": 2.0,
        },
    },
    "Acoustic Cafe": {
        "example": {
            "genre": "folk", "mood": "relaxed", "energy": 0.35, "likes_acoustic": True,
        },
        "description": "Relaxed acoustic listening, cozy and organic sound",
        "weights": {
            "genre": 2.0, "mood": 2.0, "energy": 1.5, "valence": 1.5,
            "acoustic": 3.0, "popularity": 0.2, "decade": 0.3, "detailed_mood": 1.0,
        },
    },
    "Party Mode": {
        "example": {
            "genre": "hip-hop", "mood": "hype", "energy": 0.90, "likes_acoustic": False,
        },
        "description": "High energy social listening, danceability and fun",
        "weights": {
            "genre": 2.0, "mood": 2.5, "energy": 2.5, "valence": 1.5,
            "acoustic": 0.0, "popularity": 1.0, "decade": 0.3, "detailed_mood": 1.0,
        },
    },
}


def _profile_similarity(user_prefs: dict, example: dict) -> float:
    """Compute a 0.0 to 1.0 similarity score between user prefs and a persona example."""
    score = 0.0
    total = 5.5

    if user_prefs.get("genre", "").lower() == example.get("genre", "").lower():
        score += 2.0
    if user_prefs.get("mood", "").lower() == example.get("mood", "").lower():
        score += 2.0

    energy_diff = abs(float(user_prefs.get("energy", 0.5)) - float(example.get("energy", 0.5)))
    score += (1.0 - energy_diff)

    if user_prefs.get("likes_acoustic", False) == example.get("likes_acoustic", False):
        score += 0.5

    return round(score / total, 2)


def detect_persona(user_prefs: dict) -> Tuple[str, float]:
    """Return the name and similarity score of the best matching persona."""
    best_name = ""
    best_score = -1.0
    for name, data in PERSONAS.items():
        sim = _profile_similarity(user_prefs, data["example"])
        if sim > best_score:
            best_score = sim
            best_name = name
    return best_name, best_score


def get_persona_weights(persona_name: str) -> Dict:
    """Return the specialized scoring weights for a given persona."""
    return PERSONAS[persona_name]["weights"]
