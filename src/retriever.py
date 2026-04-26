"""
Multi-source retrieval layer for VibeFinder.

Loads song catalogs from one or more CSV files and merges them into a
single deduplicated list. This is the RAG retrieval step: instead of
scoring a fixed catalog, the system first retrieves candidates from
multiple sources before passing them to the scorer.
"""

import csv
import os
from typing import List, Dict


def load_catalog(csv_path: str) -> List[Dict]:
    """Load songs from a single CSV catalog file."""
    songs = []
    if not os.path.exists(csv_path):
        print(f"  [retriever] Catalog not found, skipping: {csv_path}")
        return songs
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
                "source":         os.path.basename(csv_path),
            })
    return songs


def retrieve_from_sources(sources: List[str]) -> List[Dict]:
    """
    Load and merge songs from multiple catalog sources.
    Deduplicates by (title, artist) so overlapping catalogs stay clean.
    """
    seen = set()
    merged = []
    for path in sources:
        for song in load_catalog(path):
            key = (song["title"].lower(), song["artist"].lower())
            if key not in seen:
                seen.add(key)
                merged.append(song)
    print(f"  [retriever] Retrieved {len(merged)} songs from {len(sources)} source(s).")
    return merged
