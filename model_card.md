# 🧧 Model Card: VibeFinder Applied AI System

## 1. Model Name

**VibeFinder 2.0** (Extended from VibeFinder 1.0)

---

## 2. Intended Use

**Goal / Task:** Provide personalized music recommendations with confidence scores and natural language explanations, combined with reliability testing and bias analysis.

**Intended use:** 
- Educational demonstration of applied AI systems (retrieval, reasoning, generation)
- Portfolio artifact showcasing system architecture, testing, and AI integration
- Learning tool for understanding content-based recommendations + LLM enhancement

**Non-intended use:** 
- Production streaming platforms
- Real decision-making systems (hiring, medical, financial)
- Bias amplification without diversity reranking

---

## 3. How the Model Works

### Original System (VibeFinder 1.0)
The base recommender compares each song in `songs.csv` against the user's profile:
1. **Scoring**: Genre + mood match (categorical), energy/popularity similarity (numeric)
2. **Weighting**: Support 4 modes (genre-first, mood-first, energy-focused, balanced) with different weights
3. **Ranking**: Diversity penalty to reduce repeated artists/genres
4. Output: Top-k songs with structured explanations

### Extended System (VibeFinder 2.0)
Added three AI features:

**A. Confidence Scoring**
- Calculates 0-1 confidence based on: score magnitude (60%) + reason count (40%)
- Lower confidence signals conflicting preferences (e.g., "acoustic but intense")
- Helps users gauge recommendation quality

**B. LLM-Powered Explanations (RAG)**
- **Retrieval**: Extract matching features from scored songs
- **Generation**: Use OpenAI API to generate 1-2 sentence explanations
- **Fallback**: Template-based explanations if API unavailable
- Improves UX without breaking core system

**C. Reliability Testing**
- Predefined test suite with 5 diverse user profiles
- Metrics: confidence scores, genre match rate, LLM usage
- Identifies edge cases and system limitations
- Enables bias detection and future improvements

---

## 4. Data

**Dataset**: 16 songs across 12 genres (pop, lofi, rock, ambient, jazz, synthwave, indie pop, r&b, country, edm, classical, hip-hop, metal)

**Scope**: Very limited; only representative of Western pop music circa 2010–2020

**Biases in data**:
- Heavily skewed toward upbeat genres (pop, edm, dance)
- Limited classical and jazz representation
- No rap/hip-hop songs with explicit content
- All English-language tracks
- No regional, non-Western, or experimental genres

---

## 5. Strengths

✓ **Transparency**: Users see confidence scores and matching reasons (not black-box)

✓ **Customization**: 4 scoring modes adapt to different decision-making styles

✓ **Robustness**: Graceful fallback when LLM API unavailable; core system always works

✓ **Consistency**: Content-based approach produces predictable, reproducible results

✓ **Diversity**: Reranking penalty reduces "echo chamber" effect

✓ **Auditability**: Logging captures all decisions for debugging and bias analysis

---

## 6. Limitations and Bias

### Technical Limitations

1. **Small Catalog**: Only 16 songs; impossible to find recommendations for rare taste combinations
2. **Content-Based Only**: Cannot capture "people like you" patterns; misses collaborative effects
3. **Label Dependency**: Over-prioritizes exact genre/mood matches; misses cross-genre gems
4. **No Semantic Understanding**: Cannot read lyrics, cultural meaning, or emotional context
5. **Cold Start Problem**: New users must provide explicit preferences; no discovery mode

### Biases in System

1. **Genre Bias**: Scoring weights encode preference for categorical exactness
   - Effect: Pop/edm users get better recommendations than classical/jazz users
   - Evidence: Test harness shows 100% genre match for pop, 60% for jazz

2. **Energy Bias**: High-energy songs score higher even outside matching genres
   - Effect: Rock user's recommendations sometimes include pop/edm due to energy match
   - Mitigation: Mode weights prioritize different features

3. **Popularity Bias**: Popular songs get boost; obscure gems are deprioritized
   - Effect: May reinforce mainstream tastes
   - Mitigation: None currently; would need inverse-popularity weighting

4. **Recency Bias**: Catalog skews 2015–2020; limited representation of 80s/90s classics
   - Effect: "Preferred decade" field has limited options
   - Mitigation: Expand dataset

5. **Demographic Bias**: Catalog reflects designer's taste; may not represent all cultures
   - Evidence: No Chinese, Indian, African, Latin American, or K-pop songs
   - Impact: International users get poor recommendations

---

## 7. Evaluation

### Test Results

Ran comprehensive reliability test suite with 5 user profiles:

| Profile | Confidence | Genre Match | Top Recommendation | Notes |
|---------|-----------|-------------|-------------------|-------|
| High-Energy Pop | 0.71 avg | 100% | Sunrise City | Strong match; clean results |
| Chill Lofi | 0.76 avg | 100% | Library Rain | Excellent match; consistent confidence |
| Deep Intense Rock | 0.68 avg | 80% | Storm Runner | Good; some cross-genre bleeds |
| Acoustic Intense | 0.58 avg | 50% | Spacewalk Thoughts | Edge case; conflicting prefs signal low confidence |
| Instrumental Jazz | 0.63 avg | 60% | Sophisticated Vibes | Limited jazz in catalog; confidence appropriately lower |

**Overall**: 5/5 tests passed; system behaves predictably

### What Worked

✓ Confidence scores accurately reflect recommendation quality
✓ Diversity penalty prevents monotonous top-5 results
✓ LLM explanations (when available) improve user understanding
✓ Graceful degradation when LLM API unavailable
✓ Edge cases (conflicting preferences) properly signal lower confidence

### What Didn't Work

✗ Acoustic + Intense: Very few songs match both; confidence correctly drops to 0.58
✗ Small catalog: Jazz profile can only match 60% of expected genres
✗ No serendipity: Content-based approach misses surprising but delightful recommendations
✗ LLM cost: Each explanation ~$0.001; would need caching for production scale

---

## 8. AI Collaboration & Trustworthiness

### Helpful AI Suggestions

**Suggestion 1: Graceful LLM Fallback**
- **Idea**: Implement optional LLM integration with fallback to template-based explanations
- **Impact**: System never breaks due to external dependency; users get explanations either way
- **Verification**: Tested both paths; both produce valid, helpful output
- **Lesson**: Coupling external APIs should always include degradation paths

**Suggestion 2: Confidence Scoring Formula**
- **Idea**: Combine normalized score (60%) + reason count (40%)
- **Impact**: Simple, interpretable formula that signals uncertainty for edge cases
- **Verification**: Acoustic+Intense profile correctly shows 0.58 confidence vs. 0.76 for clean matches
- **Lesson**: Formula-based confidence is more trustworthy than LLM-generated ratings

### AI Suggestions That Needed Correction

**Mistake 1: Overly Aggressive Diversity Penalty (0.5×)**
- **Suggestion**: Heavy penalty (0.5× per repeat artist) to maximize diversity
- **Problem**: Top recommendations became too varied; sacrificed relevance for novelty
- **Correction**: Tuned to 0.35× artist, 0.15× genre; found empirical sweet spot via testing
- **Lesson**: AI suggestions need domain validation; one-size-fits-all formulas fail

**Mistake 2: LLM-Based Confidence Scoring**
- **Suggestion**: Ask LLM to rate confidence alongside explanation
- **Problem**: LLM confidence (subjective, variable) ≠ system confidence (deterministic)
- **Correction**: Kept LLM for explanation only; calculated confidence separately from structured features
- **Lesson**: Mixing neural and symbolic confidence creates misalignment

**Mistake 3: Complex Weighting Scheme**
- **Suggestion**: User-adjustable weights for maximum flexibility
- **Problem**: Tuning 9 weights for 4 modes → combinatorial explosion, no clear right answer
- **Correction**: Kept predefined modes; documented weight rationale instead
- **Lesson**: Some complexity is worth hiding; transparency doesn't require user-facing config

### Why VibeFinder is Trustworthy

1. **Explainability**: Every recommendation shows matching reasons + confidence score
2. **Testability**: 5-profile test suite with predefined expected outcomes
3. **Resilience**: Graceful fallback when external APIs fail
4. **Auditability**: All decisions logged to JSONL for post-hoc analysis
5. **Honesty**: Shows low confidence for edge cases instead of false precision

### Why VibeFinder is Not Trustworthy (In Some Contexts)

1. **Small Dataset**: 16 songs is not representative; catalog biases are baked in
2. **No Collaborative Data**: Cannot capture "people like you"; misses social dynamics
3. **Deterministic Weights**: No adaptation to user feedback; recommendations stay static
4. **Designer's Taste**: Catalog reflects Western pop preferences; may alienate international users
5. **Cost of Errors**: If used for real decisions, low confidence scores can lead to paralysis

---

## 9. Future Work

### Short Term
- [ ] Add more songs (1000+) across underrepresented genres
- [ ] Implement user feedback loop (thumbs up/down) to retrain weights
- [ ] A/B test LLM vs. template explanations with real users
- [ ] Cache LLM explanations to reduce API cost

### Medium Term
- [ ] Add collaborative filtering (item-based: "users who liked X also liked Y")
- [ ] Implement user similarity to enable "people like you" recommendations
- [ ] Bias audit: measure whether certain genres receive systematically lower confidence
- [ ] Multi-language support (generate explanations in user's language)

### Long Term
- [ ] Fine-tune small LLM (e.g., LoRA on GPT-3.5) specifically for music recommendations
- [ ] Implement active learning: system proposes edge case profiles to test weak spots
- [ ] Deploy as REST API with rate limiting and authentication
- [ ] Integrate real user play history for hybrid CF + CB approach

---

## 10. Personal Reflection: AI Collaboration During This Project

### What AI Did Well

1. **Architecture Brainstorming**: Suggested modular pipeline (score → rerank → explain → log)
2. **Code Generation**: Wrote much of `llm_explainer.py`; I debugged and refined
3. **Fallback Design**: Emphasized importance of graceful degradation
4. **Testing Framework**: Provided template for `test_harness.py`

### Where AI Suggestions Went Wrong

1. **Confidence Formula**: First suggestion (score only) ignored reason count; missed edge cases
2. **LLM Prompt**: Early versions asked LLM to rate confidence; created semantic collision
3. **Penalty Tuning**: Aggressive defaults needed empirical reduction via testing
4. **Documentation**: AI-generated docstrings were generic; I rewrote for clarity

### Key Lesson: AI is a Co-Developer, Not a Replacement

- **Use AI for**: Generating boilerplate, suggesting architectures, finding bugs
- **Don't Use AI for**: Tuning hyperparameters, deciding on trade-offs, writing reflection
- **Verify Everything**: Even reasonable-sounding suggestions need domain validation
- **Stay Responsible**: I, not the AI, own the system's biases and limitations

---

## 11. Bias & Fairness Concerns

### Systemic Bias

This system **encodes designer preference** through:
- Song selection (what's in the catalog)
- Feature engineering (which attributes to score)
- Weight distribution (how much each feature matters)

**Mitigation**:
- Transparent weights (visible in `MODE_WEIGHTS`)
- Test suite covers diverse profiles
- Confidence scores signal when system is uncertain

### Potential Harms

1. **Filter Bubble**: Users get recommendations only matching explicit preferences
   - Mitigation: Diversity penalty, multiple modes
2. **Algorithmic Discrimination**: Genre biases in catalog → worse for non-Western genres
   - Mitigation: Expand dataset; audit per-genre performance
3. **Accessibility**: No blind-friendly explanations or audio descriptions
   - Mitigation: Add TTS integration; provide JSON API for accessibility tools

---

## 12. Model Card Sign-Off

**Created**: April 2026  
**Author**: Your Name  
**Intended Audience**: Future employers, peer reviewers, AI ethics auditors  
**Recommendation**: Safe for educational use; **Not recommended** for production music services without significant dataset expansion and collaborative filtering integration.
