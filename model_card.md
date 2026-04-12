# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 suggests up to 5 songs from an 18-song catalog based on a user's preferred genre, mood, energy level, and acoustic preference. It is designed for classroom exploration of content-based filtering — not for real-world deployment. The system assumes the user can clearly state their taste as structured preferences (genre, mood, energy number). It does not learn from listening history or adapt over time.

---

## 3. How the Model Works

For every song in the catalog, the system calculates a relevance score by comparing the song's attributes to the user's stated preferences:

- If the song's **genre** matches what the user wants, it earns the most points (3.0) — because genre is the broadest signal of taste.
- If the song's **mood** matches, it earns the second-most points (2.0) — because mood reflects what the user wants right now.
- **Energy** is scored by closeness: a song that is very close to the user's target energy earns up to 1.5 points. A song far away earns less.
- **Valence** (how musically "positive" a song feels) is similarly scored by closeness, worth up to 1.0 points.
- If the user likes acoustic music and the song is highly acoustic, it earns a small bonus (0.5 points).

All songs are then ranked from highest to lowest score, and the top 5 are returned as recommendations.

---

## 4. Data

The catalog contains 18 songs stored in `data/songs.csv`. Each song has 10 attributes: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, and acousticness.

Genres represented: pop, lofi, rock, ambient, jazz, synthwave, indie pop, country, hip-hop, classical, metal, reggae, blues, edm, folk.

Moods represented: happy, chill, intense, relaxed, moody, focused, hype.

The original starter file had 10 songs — 8 more were added to increase genre and mood diversity. Despite this, several genres have only one representative song (e.g., metal, blues, classical, folk), which limits recommendations for users who prefer those genres. The data reflects a general Western pop-leaning catalog and does not represent global music styles.

---

## 5. Strengths

The system works well for users whose preferences align with well-represented genres like pop and lofi, which have multiple songs in the catalog. For a "Chill Lofi" profile, the top two results (Library Rain, Midnight Coding) were both lofi/chill with very close energy values — the recommendations felt immediately correct. The scoring logic is fully transparent: every recommendation comes with a "Why" explanation showing exactly which features contributed points, making the system easy to audit and understand.

---

## 6. Limitations and Bias

**Genre lock-in:** The genre weight (3.0) is so dominant that a song with a perfect mood and energy match in the wrong genre will almost never beat a mediocre same-genre song. This creates a "genre bubble" — users effectively only see their stated genre unless the catalog has no matches at all.

**Underrepresented genres:** Genres like blues, classical, and folk each have only one song in the catalog. A user who prefers blues will get one blues result and four unrelated songs filling the remaining slots — the system cannot meaningfully serve them.

**No mood called "sad":** The dataset has no "sad" mood. A user profile with `mood: sad` gets zero mood-match points for every song, so the system falls back entirely on energy and valence proximity — essentially ignoring the user's emotional state.

**Catalog size:** With only 18 songs, even a well-matched profile may exhaust relevant options by #3 or #4, and the remaining recommendations are filler based only on numerical proximity.

**No behavioral feedback:** The system treats every user identically regardless of history. There is no mechanism to learn from skips, replays, or likes — so it cannot personalize over time.

---

## 7. Evaluation

Four profiles were tested:

**High-Energy Pop (genre=pop, mood=happy, energy=0.9):** Results felt correct. Sunrise City ranked #1 with a score of 7.24 — it matched genre, mood, and had near-identical energy (0.82 vs. 0.9 target). Gym Hero ranked #2 with genre match but wrong mood, which made sense. The system clearly differentiated the two pop songs.

**Chill Lofi (genre=lofi, mood=chill, energy=0.38, likes_acoustic=True):** This profile produced the most satisfying results. Library Rain and Midnight Coding scored nearly identically (~7.8) at the top, both matching genre, mood, and energy closely. The acoustic bonus correctly boosted lofi tracks over others.

**Intense Rock (genre=rock, mood=intense, energy=0.95):** Only one rock song exists (Storm Runner), so #1 was clear. The surprise was #3: Iron Curtain (metal, intense) scored lower than Gym Hero (pop, intense) despite being a more intuitive match — because valence pulled Gym Hero slightly higher. This exposed how valence can over-influence rankings when genre doesn't match.

**Edge Case — Conflicting Prefs (genre=ambient, mood=hype, energy=0.92):** This is the most revealing test. Ambient and hype are contradictory (ambient songs are typically very low energy). The system picked Spacewalk Thoughts (#1) for the genre match even though it has energy 0.28 — the opposite of the 0.92 target. This is a real failure mode: the genre weight is so strong that it overrides the energy signal entirely for rare genres.

**Weight Experiment:** Halving the genre weight (3.0 → 1.5) and doubling energy (1.5 → 3.0) caused Rooftop Lights to jump above Gym Hero in the pop/happy profile, because its energy (0.76) was closer to the 0.9 target than Gym Hero's energy (0.93). This shows the rankings are sensitive to weight choices — there is no objectively "correct" weighting, only tradeoffs.

---

## 8. Future Work

- **More songs per genre:** Adding 5+ songs per genre would make recommendations meaningful for users outside pop/lofi.
- **Mood vocabulary expansion:** Adding moods like "sad," "romantic," or "nostalgic" would make user profiles more expressive.
- **Diversity enforcement:** The current system can return the same artist twice. A diversity rule (e.g., max 1 song per artist in top 5) would improve variety.
- **Behavioral memory:** Even a simple "disliked genres" list on the user profile would let the system filter out bad matches.
- **Hybrid approach:** Combining this content-based scorer with a simple collaborative signal (e.g., "users who liked X also liked Y") would dramatically improve result quality.

---

## 9. Personal Reflection

Building VibeFinder made it clear that a recommendation system is only as good as its weights — and choosing those weights is a judgment call, not a math problem. The weight experiment showed that shifting genre from 3.0 to 1.5 meaningfully changed the order of results, and both orderings had a reasonable argument. Real platforms like Spotify likely tune these weights using millions of data points and A/B tests, not intuition.

The most surprising finding was the edge case profile: combining "ambient" genre with "hype" mood and 0.92 energy broke the system's logic completely. It returned a quiet ambient track as the top result because genre won over everything else. This showed that content-based filtering assumes the user's preferences are internally consistent — and real users often aren't. That's probably why Spotify doesn't just ask you to fill out a form; it watches what you actually do.
