# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder 1.0 tries to predict which songs from a small catalog a user will enjoy based on their stated taste preferences. Given a user's favorite genre, mood, target energy level, and acoustic preference, it scores every song and returns the top 5 most relevant matches. It is a simulation of how content-based filtering works, not a production recommendation engine.

---

## 3. Data Used

- **Dataset:** `data/songs.csv` with 18 songs (expanded from the original 10)
- **Features per song:** genre, mood, energy (0.0 to 1.0), tempo_bpm, valence (0.0 to 1.0), danceability (0.0 to 1.0), acousticness (0.0 to 1.0)
- **Genres covered:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, country, hip-hop, classical, metal, reggae, blues, edm, folk
- **Moods covered:** happy, chill, intense, relaxed, moody, focused, hype
- **Limits:** Several genres (blues, classical, folk, metal) have only one song each. The catalog does not represent global or non-Western music. There is no "sad" mood in the dataset. All data was hand-crafted for the simulation and does not reflect real listening behavior.

---

## 4. Algorithm Summary

For every song in the catalog, the system calculates a score by asking five questions:

1. **Does the genre match?** If yes, the song earns 3.0 points. Genre is the strongest signal of musical taste.
2. **Does the mood match?** If yes, it earns 2.0 points. Mood reflects what the user wants to feel right now.
3. **How close is the energy?** A song with energy very close to the user's target earns up to 1.5 points. The farther away it is, the fewer points it gets.
4. **How close is the valence?** Valence measures how musically positive a song feels. Closeness to a default target of 0.7 earns up to 1.0 points.
5. **Acoustic bonus:** If the user likes acoustic music and the song is highly acoustic, it earns an extra 0.5 points.

All songs are ranked from highest to lowest score and the top 5 are returned.

---

## 5. Observed Behavior and Biases

**Genre dominance (filter bubble):** The genre weight (3.0) is high enough that a song with a perfect mood and energy match in the wrong genre almost never beats a mediocre same-genre song. Users get trapped in a genre bubble and the system rarely surfaces something unexpected.

**Rare genre failure:** Users who prefer blues, classical, or folk only get one relevant result. The other four recommendations are unrelated songs that happen to score well on energy and valence proximity, not true matches.

**Conflicting preferences break the system:** The edge case profile (ambient genre, hype mood, high energy 0.92) returned Spacewalk Thoughts as the top result even though it has energy 0.28, purely because of the genre match. The system cannot handle contradictory user inputs. It just weighs the categories and picks a winner, even when the winner makes no sense.

**No "sad" mood:** Because the dataset lacks a "sad" mood entry, any user who wants melancholic music gets zero mood-match points across every song. The system effectively ignores their emotional preference entirely.

**Valence surprises:** Iron Curtain (metal, intense) ranked below Gym Hero (pop, intense) for the Intense Rock profile because Gym Hero's valence (0.77) is closer to the 0.7 default than Iron Curtain's (0.21). A metal song being beaten by a pop song for a rock user is a clear failure of the valence scoring logic.

---

## 6. Evaluation Process

Four user profiles were tested:

- **High-Energy Pop** (pop / happy / 0.9 energy): Results felt correct. Sunrise City ranked first and matched genre, mood, and energy. Gym Hero ranked second with genre but the wrong mood, which made sense given the score gap.
- **Chill Lofi** (lofi / chill / 0.38 energy / likes_acoustic=True): Best-performing profile. Top two songs (Library Rain, Midnight Coding) scored nearly identically around 7.8 and both felt like the right recommendation. Acoustic bonus worked as intended.
- **Intense Rock** (rock / intense / 0.95 energy): Only one rock song in the catalog (Storm Runner), so first place was obvious. The surprise was Iron Curtain (metal) ranking below Gym Hero (pop) at third place, which exposed the valence scoring flaw.
- **Edge Case** (ambient / hype / 0.92 energy / likes_acoustic=True): A deliberate contradiction. Revealed that genre weight dominates all other signals when a rare genre matches, even when every other attribute is wrong.

**Weight experiment:** Halved the genre weight (3.0 to 1.5) and doubled energy weight (1.5 to 3.0). For the pop/happy profile, Rooftop Lights jumped from third to second because its energy was closer to the target. Confirmed the system is sensitive to weight choices and there is no single correct weighting.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- Classroom exploration of how content-based filtering works
- Learning how weighted scoring turns structured data into ranked recommendations
- Demonstrating algorithmic bias and filter bubbles in a simple, transparent system

**Not intended for:**
- Real music recommendation in a product or app
- Serving users with complex, evolving, or contradictory tastes
- Replacing systems that learn from actual listening behavior
- Any catalog larger than a few dozen songs without significant redesign

---

## 8. Ideas for Improvement

1. **Expand the catalog and balance genres.** Adding 5+ songs per genre would make recommendations meaningful for users outside pop and lofi. Right now, rare-genre users get poor results no matter how good the scoring logic is.

2. **Add mood vocabulary.** Including moods like "sad," "romantic," and "nostalgic" would let the system serve a much wider range of emotional states instead of silently ignoring them.

3. **Cap genre dominance with a diversity rule.** Limiting the genre weight or enforcing a maximum of one song per artist in the top 5 would reduce the filter bubble effect and surface more varied results.

---

## 9. Personal Reflection

The biggest learning moment in this project was the edge case experiment. I expected the adversarial profile (ambient, hype, high energy) to produce a weird mix of songs. Instead it confidently returned a quiet ambient track as the top recommendation because of the genre match. That moment made it clear that confidence and correctness are not the same thing in an algorithm. The system was doing exactly what it was told. It just did not know that the user's preferences were contradictory.

Using AI tools helped most during the design phase, working through the scoring logic, thinking about weights, and identifying what kinds of bias might appear before writing a single line of code. The part that required more careful checking was the weight experiment. It was easy to make a change and see different numbers, but understanding why Rooftop Lights jumped above Gym Hero required going back to the math and tracing the scores manually.

The most surprising thing about the project was how the results can feel like real recommendations even though the system is just adding up five numbers. For the Chill Lofi profile, the top two results genuinely felt like what you would want to hear in a library. That feeling comes entirely from the weights being reasonable, not from any deep understanding of music. It is a good reminder that a lot of what makes AI feel intelligent is careful design of simple rules, not magic.

If I extended this project, I would add a feedback loop. Even a simple thumbs up or thumbs down on each recommendation that adjusts the user's profile weights over time would turn a static content-based filter into something that actually learns, which is closer to how Spotify's Taste Profile works in practice.
