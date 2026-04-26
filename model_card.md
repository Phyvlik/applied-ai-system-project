# Model Card: VibeFinder 2.0

## 1. Model Name

**VibeFinder 2.0**

Base project: VibeFinder 1.0, built for Module 3 of AI110.

---

## 2. Goal and Task

VibeFinder 2.0 takes a user's stated music preferences (genre, mood, energy level, acoustic
taste, decade, and detailed mood) and returns the top 5 most relevant songs from an 18-song
catalog. It uses a weighted content-based filtering algorithm, applies a diversity penalty
to avoid repetitive results, and runs input and output guardrails to catch bad data and
low-confidence results. An automated evaluation harness verifies consistent behavior across
8 predefined test cases.

This is a simulation of how content-based recommendation systems work, not a production engine.

---

## 3. Data Used

- **Dataset:** `data/songs.csv` with 18 songs
- **Features per song:** genre, mood, energy, tempo_bpm, valence, danceability, acousticness,
  popularity, release_decade, detailed_mood, explicit, instrumental
- **Genres covered:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, country, hip-hop,
  classical, metal, reggae, blues, edm, folk
- **Moods covered:** happy, chill, intense, relaxed, moody, focused, hype
- **Limits:** Several genres have only one song each. The catalog does not represent global
  or non-Western music. There is no "sad" mood. All data was hand-crafted for the simulation
  and does not reflect real listening behavior.

---

## 4. Algorithm Summary

For every song in the catalog, the system calculates a score across up to ten signals:

1. **Genre match** - earns up to 3.0 points depending on scoring mode
2. **Mood match** - earns up to 3.0 points depending on scoring mode
3. **Energy proximity** - closer to target earns more, up to 1.5 points
4. **Valence proximity** - closeness to a 0.7 default earns up to 1.0 point
5. **Acoustic bonus** - +0.5 if user likes acoustic and song has high acousticness
6. **Popularity bonus** - +0.3 for songs rated 75 or above
7. **Decade match** - +0.3 if song release decade matches user preference
8. **Detailed mood match** - up to 1.5 points for fine-grained mood tags
9. **Explicit penalty** - -2.0 if user has avoid_explicit=True and song is explicit
10. **Instrumental bonus** - +0.5 for users who prefer instrumental tracks

Three scoring modes shift which signal is weighted highest: genre-first, mood-first,
and energy-focused. A diversity filter then limits the top 5 to one song per artist
and two per genre before results are displayed.

---

## 5. Limitations and Biases

**Genre dominance (filter bubble):** The genre weight is high enough that a song with a
perfect mood and energy match in the wrong genre almost never beats a mediocre same-genre
song. Users get locked into a genre bubble and the system rarely surfaces anything outside
their stated preference.

**Rare genre failure:** Users who prefer blues, classical, or folk only get one relevant
result. The other four recommendations are unrelated songs that happen to score well on
energy and valence proximity, not true matches.

**Conflicting preferences break the system:** The edge case profile (ambient genre, hype
mood, high energy 0.92) returned Spacewalk Thoughts as the top result even though it has
energy 0.28, purely because of the genre match. The system cannot handle contradictory
inputs. It weighs the signals and picks a winner, even when that winner makes no sense.

**No "sad" mood:** Because the dataset lacks a sad mood entry, any user who wants
melancholic music gets zero mood-match points across every song. The system silently
ignores their emotional preference.

**Valence surprises:** Iron Curtain (metal, intense) ranked below Gym Hero (pop, intense)
for the Intense Rock profile because Gym Hero's valence is closer to the 0.7 default.
A metal song losing to a pop song for a rock user is a clear failure of the valence logic.

**Catalog imbalance reflects real bias:** With only 18 songs, pop and lofi users get
strong results while niche genre users do not. This mirrors how real recommendation
systems underserve niche and non-Western audiences when training data is skewed toward
mainstream content.

---

## 6. Could This System Be Misused?

A music recommender seems low-stakes, but the pattern this system uses can be applied to
higher-stakes domains, which creates real risks.

**Filter bubble amplification:** Any system that reinforces a user's stated preferences
without ever challenging them can deepen echo chambers over time. In music this means
never discovering new genres. In news or social media the same algorithm design contributes
to radicalization and misinformation spread.

**Proxy discrimination:** If the catalog were a job applicant pool and the user profile
were a hiring manager's preferences, this exact algorithm would encode and amplify bias.
A "genre match" becomes a demographic match. The system would confidently surface
candidates that look like previous hires and penalize everyone else.

**False confidence:** The system displays scores and explanations that look authoritative.
A user might trust a 6.7-scored recommendation without realizing the score is based on
five simple rules applied to hand-crafted data.

**How I would prevent misuse:**
- Display a clear disclaimer that results reflect the catalog and weights, not objective quality
- The confidence guardrail already warns users when scores are low, which is one honest signal
- Any real deployment would need a bias audit of the catalog before launch
- I would never use this scoring pattern in hiring, lending, or any domain with legal accountability

---

## 7. What Surprised Me During Testing

I expected the edge case profile to fail in an obvious way, like returning completely
unrelated songs. What surprised me was that it failed confidently. Spacewalk Thoughts had
a clean score and a readable explanation. Nothing in the output looked wrong unless you
already knew the user wanted high-energy hype music. That gap between looking correct and
being correct is what the confidence guardrail is meant to address, but it only catches
the worst cases. A score of 4.5 still feels trustworthy even when the result is bad.

The other surprise was the Intense Rock profile. I assumed a rock user asking for intense
music would get metal in the top three. Instead, Gym Hero (a pop song) ranked above Iron
Curtain (metal) because valence proximity favored the pop track. I had not thought through
how valence interacts with genre until I saw that result. It changed how I think about
feature weighting: adding more features does not always improve results. Sometimes it
introduces unexpected interactions that are harder to control than the original system.

---

## 8. AI Collaboration

I used AI assistance throughout this project for design, debugging, and decision-making.

**One instance where AI gave a helpful suggestion:**

When I was thinking about the reliability component for this version, AI suggested
structuring the guardrails as two separate functions: one for input validation before
scoring runs, and one for output confidence after scoring completes. I had originally
been thinking of them as one block at the end. Splitting them made the logic cleaner
and made the tests easier to write, because each function has a single responsibility.
That suggestion improved the design in a way I would not have landed on as quickly alone.

**One instance where AI's suggestion was flawed:**

Early on, AI suggested adding the Claude API to generate natural language explanations
for the recommendations, framing it as the "substantial new AI feature" the rubric asked
for. That suggestion was technically interesting but wrong for this project. It would
have required an API key and spending money, the rubric does not require a paid API,
and the guardrails plus evaluation harness already satisfy the reliability harness
requirement without any external dependency. Following that suggestion would have added
complexity, cost, and a dependency that could break the demo if the key expired. I
pushed back and we scoped it out, which was the right call.

---

## 9. Evaluation Results

**Unit tests:** 11/11 passed
- test_recommender.py: 2 tests covering core scoring and explanation output
- test_guardrails.py: 9 tests covering valid inputs, each error type, multiple simultaneous
  errors, empty fields, and both confidence thresholds

**Evaluation harness:** 8/8 passed (100% pass rate)
- Pop/Happy genre match: PASS
- Lofi/Chill genre match: PASS
- Rock/Intense genre match: PASS
- EDM/Hype genre match: PASS
- Unknown genre triggers guardrail: PASS
- Out-of-range energy triggers guardrail: PASS
- Valid prefs return 5 results: PASS
- Diversity constraint enforced: PASS

**Four user profiles tested manually:**
- High-Energy Pop: results felt correct, Sunrise City ranked first
- Chill Lofi: best-performing profile, top two results both felt like the right call
- Intense Rock: exposed the valence flaw (Gym Hero above Iron Curtain)
- Edge Case: exposed genre weight dominance (quiet ambient track ranked first for hype user)

---

## 10. Intended and Non-Intended Use

**Intended use:**
- Learning how content-based filtering and weighted scoring work
- Demonstrating algorithmic bias and filter bubbles in a transparent, inspectable system
- Classroom exploration of recommendation system design and trade-offs

**Not intended for:**
- Real music recommendation in a product
- Serving users with complex, evolving, or contradictory tastes
- Any catalog larger than a few dozen songs without significant redesign
- Any domain involving consequential decisions (hiring, lending, healthcare)

---

## 11. Ideas for Improvement

1. **Expand the catalog and balance genres.** Adding 5+ songs per genre would make
   recommendations meaningful for niche-genre users.

2. **Add a feedback loop.** Even a simple thumbs up or down that adjusts weights over
   time would turn this into something that actually learns from behavior.

3. **Add a "sad" mood and broader mood vocabulary.** The current mood set is too narrow
   and silently ignores large parts of how people actually want to feel when listening.

4. **Cap genre weight or add a surprise factor.** A small probability of surfacing a
   song from outside the user's genre would reduce filter bubble effects.
