import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """Represents a song and its audio attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: str = ""
    detailed_mood: str = ""
    explicit: bool = False
    instrumental: bool = False


@dataclass
class UserProfile:
    """Represents a user's taste preferences for content-based filtering."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Challenge 2: Scoring mode weights
# Each mode is a dict of feature -> weight multiplier applied on top of base logic.
# ---------------------------------------------------------------------------

SCORING_MODES = {
    "genre-first": {
        "genre":   3.0,
        "mood":    1.5,
        "energy":  1.0,
        "valence": 0.5,
        "acoustic":0.5,
        "popularity": 0.3,
        "decade":  0.3,
        "detailed_mood": 1.0,
    },
    "mood-first": {
        "genre":   1.5,
        "mood":    3.0,
        "energy":  1.0,
        "valence": 1.0,
        "acoustic":0.5,
        "popularity": 0.3,
        "decade":  0.3,
        "detailed_mood": 1.5,
    },
    "energy-focused": {
        "genre":   1.5,
        "mood":    1.0,
        "energy":  3.0,
        "valence": 0.5,
        "acoustic":0.5,
        "popularity": 0.3,
        "decade":  0.3,
        "detailed_mood": 0.5,
    },
}

DEFAULT_MODE = "genre-first"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file, converting numeric fields to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":             int(row["id"]),
                "title":          row["title"],
                "artist":         row["artist"],
                "genre":          row["genre"],
                "mood":           row["mood"],
                "energy":         float(row["energy"]),
                "tempo_bpm":      float(row["tempo_bpm"]),
                "valence":        float(row["valence"]),
                "danceability":   float(row["danceability"]),
                "acousticness":   float(row["acousticness"]),
                "popularity":     int(row["popularity"]),
                "release_decade": row["release_decade"],
                "detailed_mood":  row["detailed_mood"],
                "explicit":       row["explicit"].strip().lower() == "true",
                "instrumental":   row["instrumental"].strip().lower() == "true",
            })
    print(f"Loaded songs: {len(songs)}")
    return songs


# ---------------------------------------------------------------------------
# Challenge 1 + 2: Scoring function with new features and mode support
# ---------------------------------------------------------------------------

def score_song(user_prefs: Dict, song: Dict, mode: str = DEFAULT_MODE) -> Tuple[float, List[str]]:
    """
    Score a single song against user preferences using weighted content-based scoring.

    Supports multiple scoring modes: genre-first, mood-first, energy-focused.
    Also scores new attributes: popularity, release_decade, detailed_mood,
    explicit filter, and instrumental preference.
    """
    weights = SCORING_MODES.get(mode, SCORING_MODES[DEFAULT_MODE])
    score = 0.0
    reasons = []

    # Genre match
    if song.get("genre", "").lower() == user_prefs.get("genre", "").lower():
        pts = weights["genre"]
        score += pts
        reasons.append(f"genre match (+{pts:.1f})")

    # Mood match
    if song.get("mood", "").lower() == user_prefs.get("mood", "").lower():
        pts = weights["mood"]
        score += pts
        reasons.append(f"mood match (+{pts:.1f})")

    # Energy proximity
    target_energy = user_prefs.get("energy", 0.5)
    energy_pts = (1 - abs(song.get("energy", 0.5) - target_energy)) * weights["energy"] * 1.5
    score += energy_pts
    reasons.append(f"energy proximity (+{energy_pts:.2f})")

    # Valence proximity (default target 0.7)
    target_valence = user_prefs.get("valence", 0.7)
    valence_pts = (1 - abs(song.get("valence", 0.5) - target_valence)) * weights["valence"]
    score += valence_pts
    reasons.append(f"valence proximity (+{valence_pts:.2f})")

    # Acoustic bonus
    if user_prefs.get("likes_acoustic", False) and song.get("acousticness", 0) > 0.6:
        pts = weights["acoustic"]
        score += pts
        reasons.append(f"acoustic bonus (+{pts:.1f})")

    # Challenge 1: Popularity bonus (songs above 75 get a small boost)
    pop = song.get("popularity", 0)
    if pop >= 75:
        pop_pts = weights["popularity"]
        score += pop_pts
        reasons.append(f"popularity bonus (+{pop_pts:.1f})")

    # Challenge 1: Decade preference
    preferred_decade = user_prefs.get("preferred_decade", "")
    if preferred_decade and song.get("release_decade", "") == preferred_decade:
        dec_pts = weights["decade"]
        score += dec_pts
        reasons.append(f"decade match (+{dec_pts:.1f})")

    # Challenge 1: Detailed mood tag match
    preferred_detailed = user_prefs.get("detailed_mood", "")
    if preferred_detailed and song.get("detailed_mood", "").lower() == preferred_detailed.lower():
        dm_pts = weights["detailed_mood"]
        score += dm_pts
        reasons.append(f"detailed mood match (+{dm_pts:.1f})")

    # Challenge 1: Explicit filter (if user sets avoid_explicit=True, penalize)
    if user_prefs.get("avoid_explicit", False) and song.get("explicit", False):
        score -= 2.0
        reasons.append("explicit penalty (-2.0)")

    # Challenge 1: Instrumental preference
    if user_prefs.get("prefers_instrumental", False) and song.get("instrumental", False):
        score += 0.5
        reasons.append("instrumental bonus (+0.5)")

    return score, reasons


# ---------------------------------------------------------------------------
# Challenge 3: Diversity penalty
# ---------------------------------------------------------------------------

def apply_diversity_penalty(
    ranked: List[Tuple[Dict, float, str]],
    max_per_artist: int = 1,
    max_per_genre: int = 2,
) -> List[Tuple[Dict, float, str]]:
    """
    Re-rank results to enforce diversity: limit songs per artist and per genre.
    Songs that violate the limits are moved to the end with a penalty note.
    """
    seen_artists: Dict[str, int] = {}
    seen_genres: Dict[str, int] = {}
    prioritized = []
    penalized = []

    for song, score, explanation in ranked:
        artist = song.get("artist", "")
        genre = song.get("genre", "")
        artist_count = seen_artists.get(artist, 0)
        genre_count = seen_genres.get(genre, 0)

        if artist_count >= max_per_artist:
            penalized.append((song, score - 1.5, explanation + " | diversity penalty: artist"))
        elif genre_count >= max_per_genre:
            penalized.append((song, score - 0.75, explanation + " | diversity penalty: genre"))
        else:
            prioritized.append((song, score, explanation))
            seen_artists[artist] = artist_count + 1
            seen_genres[genre] = genre_count + 1

    return prioritized + penalized


# ---------------------------------------------------------------------------
# Main recommendation function
# ---------------------------------------------------------------------------

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = DEFAULT_MODE,
    diversity: bool = True,
) -> List[Tuple[Dict, float, str]]:
    """
    Score and rank all songs, apply optional diversity penalty, return top-k.
    Supports scoring modes: genre-first, mood-first, energy-focused.
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode=mode)
        explanation = " | ".join(reasons)
        scored.append((song, score, explanation))

    ranked = sorted(scored, key=lambda x: x[1], reverse=True)

    if diversity:
        ranked = apply_diversity_penalty(ranked)

    return ranked[:k]


# ---------------------------------------------------------------------------
# OOP interface (required by tests)
# ---------------------------------------------------------------------------

class Recommender:
    """OOP implementation of the content-based music recommender."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score all songs against the user profile and return the top-k sorted by score."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        scored = []
        for song in self.songs:
            song_dict = {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "valence": song.valence,
                "acousticness": song.acousticness,
                "popularity": getattr(song, "popularity", 50),
                "release_decade": getattr(song, "release_decade", ""),
                "detailed_mood": getattr(song, "detailed_mood", ""),
                "explicit": getattr(song, "explicit", False),
                "instrumental": getattr(song, "instrumental", False),
            }
            score, _ = score_song(user_prefs, song_dict)
            scored.append((score, song))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [song for _, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song was recommended."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        song_dict = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "valence": song.valence,
            "acousticness": song.acousticness,
            "popularity": getattr(song, "popularity", 50),
            "release_decade": getattr(song, "release_decade", ""),
            "detailed_mood": getattr(song, "detailed_mood", ""),
            "explicit": getattr(song, "explicit", False),
            "instrumental": getattr(song, "instrumental", False),
        }
        _, reasons = score_song(user_prefs, song_dict)
        return " | ".join(reasons) if reasons else "No strong matches found."
