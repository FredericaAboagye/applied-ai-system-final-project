# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This version simulates a small music recommender that compares a user's taste profile against song features in `songs.csv`. It gives each song a weighted score based on genre, mood, energy, and acoustic fit, then ranks the strongest matches as recommendations.

---

## How The System Works

Real streaming platforms often combine **collaborative filtering** (learning from what similar users play, skip, save, and replay) with **content-based filtering** (matching the attributes of a song itself). My simulator focuses on the content-based side. It compares one user's preferences to every song in the catalog and prioritizes tracks that match the user's preferred genre and mood while also staying close to the user's target energy and acoustic vibe.

### Features used in this simulation

**`Song` fields**
- `genre`
- `mood`
- `energy`
- `tempo_bpm`
- `valence`
- `danceability`
- `acousticness`
- `popularity`
- `release_decade`
- `mood_tag`
- `instrumentalness`
- `focus_score`

**`UserProfile` fields**
- `favorite_genre`
- `favorite_mood`
- `target_energy`
- `likes_acoustic`
- `preferred_mood_tag`
- `preferred_decade`
- `target_popularity`
- `likes_instrumental`
- `target_focus`
- `mode`

### Example taste profile

```python
{
    "favorite_genre": "lofi",
    "favorite_mood": "focused",
    "target_energy": 0.40,
    "likes_acoustic": True,
}
```

This profile is specific enough to separate **intense rock** from **chill lofi** because it uses both label-based preferences (`genre`, `mood`) and vibe-based features (`energy`, `acousticness`).

### Algorithm Recipe

1. Start each song at `0` points.
2. Add more points for matching the user's preferred `genre` and `mood`.
3. Reward songs whose `energy`, `focus_score`, and `popularity` are numerically close to the user's targets.
4. Add smaller bonuses for a matching `mood_tag`, a preferred `release_decade`, and whether the user likes acoustic or instrumental tracks.
5. Let the user choose a scoring mode such as `genre-first`, `mood-first`, `energy-focused`, or `balanced`.
6. Apply a small **diversity penalty** if the same artist or genre is already appearing in the top results.
7. Sort all songs by the adjusted score and return the top `k` songs with a short explanation of why they matched.

### Why scoring and ranking both matter

- The **scoring rule** decides how well one song matches the profile.
- The **ranking rule** orders the whole catalog so the strongest matches rise to the top.

### Data Flow

```mermaid
flowchart LR
    A[User Preferences] --> B[Read songs.csv]
    B --> C[Score one song at a time]
    C --> D[Apply weights for genre, mood, energy, and acousticness]
    D --> E[Store score and explanation]
    E --> F[Rank all songs by score]
    F --> G[Return Top K recommendations]
```

### Expected bias / limitation

This system might over-prioritize **genre** and **mood**, which means it could ignore surprising songs that match the user's vibe but use a different label. It also does not use community behavior, so it misses the large-scale "people like you also loved this" effect that real streaming platforms use.

### CLI Example Output

```text
Loaded songs: 16

Top recommendations:
1. Sunrise City by Neon Echo
   Score: 4.98
   Why: genre match (+2.0); mood match (+1.5); energy similarity (+0.98); acoustic preference match (+0.5)

2. Gym Hero by Max Pulse
   Score: 3.37
   Why: genre match (+2.0); energy similarity (+0.87); acoustic preference match (+0.5)
```

![CLI output screenshot](recommender-output.png)

#### Evaluation Screenshots

![Acoustic but Intense](Acoustic%20but%20Intense.png)
![Chill Lofi](Chill%20Lofi.png)
![High-Energy Pop](High-Energy%20Pop.png)
![Deep Intense Rock](Deep%20Intense%20Rock.png)

#### Optional Extension Output

![Optional extension table output](table-output.png)

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

I tested the recommender with four different profiles:

- **High-Energy Pop** → `Sunrise City` ranked first, followed by `Gym Hero`, which made sense because both songs are upbeat and energetic.
- **Chill Lofi** → `Library Rain` and `Midnight Coding` rose to the top because they matched the lofi/chill labels and the lower energy target.
- **Deep Intense Rock** → `Storm Runner` ranked first, but `Gym Hero` and `Neon Festival` also appeared because the system strongly rewards high energy even outside the rock genre.
- **Edge Case: Acoustic but Intense** → `Spacewalk Thoughts` ranked first even though it is not very intense, which showed that the exact genre match and acoustic bonus can sometimes overpower the energy mismatch.

I also ran a **weight-shift experiment** where I doubled the importance of energy and reduced the genre weight. That made the pop profile more sensitive to raw vibe, so `Rooftop Lights` moved above `Gym Hero`. This made the results more varied, but also less strict about exact genre matching.

---

## Limitations and Risks

This recommender only works on a **small catalog of 16 songs**, so it cannot represent the full range of music taste. It also relies on a few simple features and exact matches, which means it may over-favor one genre or mood and create a small **filter bubble**. It does not understand lyrics, context, cultural meaning, or why a person likes a song beyond a few numbers and labels.

---

## Reflection

[**Model Card**](model_card.md)

This project helped me see that recommenders turn user taste into a set of weighted comparisons rather than truly “understanding” music. The output can feel smart, but it is really the result of a few rules about genre, mood, energy, and acousticness. When those rules line up with a profile like **Chill Lofi**, the recommendations feel very accurate.

I also learned how easily bias can appear in a system like this. Because the catalog is small and the weights prioritize exact genre and mood matches, some users get better recommendations than others. The edge-case profile showed that when preferences conflict, the system can produce results that are logical by the math but not fully satisfying to a human listener.

