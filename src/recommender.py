import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


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


@dataclass
class UserProfile:
    """Represents a user's taste preferences for content-based filtering."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


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
        }
        _, reasons = score_song(user_prefs, song_dict)
        return " | ".join(reasons) if reasons else "No strong matches found."


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file, converting numeric fields to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score a single song against user preferences using a weighted content-based recipe.

    Scoring rules:
      +3.0  genre match
      +2.0  mood match
      +1.5  energy proximity  (1 - |song.energy - target|) * 1.5
      +1.0  valence proximity (1 - |song.valence - 0.7|) * 1.0  (default target)
      +0.5  acoustic bonus    if likes_acoustic and acousticness > 0.6

    Returns (score, reasons) where reasons is a list of explanation strings.
    """
    score = 0.0
    reasons = []

    # Genre match
    if song.get("genre", "").lower() == user_prefs.get("genre", "").lower():
        score += 3.0
        reasons.append(f"genre match (+3.0)")

    # Mood match
    if song.get("mood", "").lower() == user_prefs.get("mood", "").lower():
        score += 2.0
        reasons.append(f"mood match (+2.0)")

    # Energy proximity
    target_energy = user_prefs.get("energy", 0.5)
    energy_points = (1 - abs(song.get("energy", 0.5) - target_energy)) * 1.5
    score += energy_points
    reasons.append(f"energy proximity (+{energy_points:.2f})")

    # Valence proximity (default target: 0.7 — moderately positive)
    target_valence = user_prefs.get("valence", 0.7)
    valence_points = (1 - abs(song.get("valence", 0.5) - target_valence)) * 1.0
    score += valence_points
    reasons.append(f"valence proximity (+{valence_points:.2f})")

    # Acoustic bonus
    if user_prefs.get("likes_acoustic", False) and song.get("acousticness", 0) > 0.6:
        score += 0.5
        reasons.append("acoustic bonus (+0.5)")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score and rank all songs, returning the top-k as (song, score, explanation) tuples."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = " | ".join(reasons)
        scored.append((song, score, explanation))

    # sorted() returns a new list; reverse=True gives highest score first
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return ranked[:k]
