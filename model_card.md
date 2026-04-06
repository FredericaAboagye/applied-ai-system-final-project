# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

This recommender is designed to suggest a small set of songs from a classroom-sized catalog based on a user's preferred genre, mood, energy level, and acoustic preference. It is meant for learning and experimentation, not for real-world production use. The model assumes that a person's musical taste can be represented by a few simple preferences.

---

## 3. How the Model Works

The model compares each song in `songs.csv` to the user's profile. It adds points for a matching genre, a matching mood, and a close energy level, and it gives a small bonus when the song's acousticness fits the user's preference. After every song gets a score, the system ranks the list from highest to lowest and returns the top recommendations along with short reasons.

---

## 4. Data

The dataset contains **16 songs**. I expanded the starter catalog to include a wider range of genres such as pop, lofi, rock, ambient, jazz, synthwave, indie pop, r&b, country, edm, classical, hip-hop, and metal. Even with those additions, the dataset is still small and only covers a limited set of moods, so it does not reflect the full range of real music taste.

---

## 5. Strengths

The recommender works best for users with clear and consistent taste profiles. For example, the **Chill Lofi** profile returned `Library Rain` and `Midnight Coding`, which felt like strong matches because they aligned with the user's genre, mood, energy, and acoustic preferences. The **High-Energy Pop** profile also behaved well by ranking `Sunrise City` and `Gym Hero` near the top.

---

## 6. Limitations and Bias

One weakness is that the system over-prioritizes exact labels like genre and mood, which can create a small filter bubble. Users with mixed or conflicting preferences, such as wanting something both intense and very acoustic, may get less satisfying results because the catalog has very few songs that fit both. The energy score is also very simple, so it cannot capture more subtle musical traits like lyrics, context, or personal memories tied to a song.

---

## 7. Evaluation

I tested four profiles: **High-Energy Pop**, **Chill Lofi**, **Deep Intense Rock**, and an edge case called **Acoustic but Intense**. The main thing I looked for was whether the top results felt believable based on my own intuition. `Sunrise City` ranked first for the pop profile, `Library Rain` ranked first for the lofi profile, and `Storm Runner` ranked first for the rock profile, which all made sense. The most surprising case was the edge profile: `Spacewalk Thoughts` ranked highly because the genre match and acoustic bonus outweighed the weaker energy fit.

I also ran a small experiment where I **doubled the importance of energy** and **reduced the genre weight**. That change made the recommendations more vibe-driven and less label-driven. For example, `Rooftop Lights` moved above `Gym Hero` for the pop profile, showing that even one weight change can noticeably shift the ranking.

---

## 8. Future Work

If I had more time, I would add more songs, more moods, and more user features so the system could handle more complex taste patterns. I would also improve diversity so the top results are not always the closest possible match on one feature. A future version could combine this content-based approach with collaborative filtering so it can learn from the behavior of similar users.

---

## 9. Personal Reflection

This project showed me that recommenders do not magically understand taste; they turn a few weighted signals into a ranking. What surprised me most was how quickly the results changed when I adjusted one weight, which made the system feel both transparent and fragile. Building it made me think more critically about real streaming apps, because even when the recommendations feel smart, human judgment still matters when deciding what is fair, diverse, and actually enjoyable.
