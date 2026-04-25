"""Test harness and evaluation script for VibeFinder reliability and performance."""

import json
import logging
import sys
from typing import Dict, List, Tuple
from pathlib import Path

try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RecommendationEvaluator:
    """Evaluate the music recommender system on predefined test cases."""
    
    def __init__(self, songs_csv: str):
        """Initialize evaluator with song catalog."""
        self.songs = load_songs(songs_csv)
        logger.info(f"Loaded {len(self.songs)} songs for evaluation")
        self.results: List[Dict] = []
    
    def run_test_case(
        self,
        test_name: str,
        user_prefs: Dict,
        expected_genres: List[str] = None,
        use_llm: bool = False,
        k: int = 5
    ) -> Dict:
        """
        Run a single test case and evaluate results.
        
        Args:
            test_name: Name of the test
            user_prefs: User preference dictionary
            expected_genres: List of genres we expect in top results
            use_llm: Whether to use LLM explanations
            k: Number of recommendations to return
        
        Returns:
            Test result dictionary with metrics
        """
        try:
            logger.info(f"Running test: {test_name}")
            
            recommendations = recommend_songs(
                user_prefs, self.songs, k=k, use_llm=use_llm
            )
            
            # Extract metrics
            scores = [rec[1] for rec in recommendations]
            confidences = [rec[3] for rec in recommendations]
            used_llm_counts = sum(1 for rec in recommendations if rec[4])
            
            # Check genre coverage if specified
            genres = [rec[0].get("genre") for rec in recommendations]
            genre_match = 0
            if expected_genres:
                genre_match = sum(1 for g in genres if g in expected_genres)
            
            result = {
                "test_name": test_name,
                "status": "PASS",
                "num_recommendations": len(recommendations),
                "avg_score": round(sum(scores) / len(scores), 2) if scores else 0,
                "avg_confidence": round(sum(confidences) / len(confidences), 2) if confidences else 0,
                "min_confidence": round(min(confidences), 2) if confidences else 0,
                "max_confidence": round(max(confidences), 2) if confidences else 0,
                "used_llm": used_llm_counts,
                "genres_returned": genres,
                "expected_genres": expected_genres or [],
                "genre_match_count": genre_match,
                "genre_match_rate": round(genre_match / len(expected_genres), 2) if expected_genres else None,
                "top_recommendation": f"{recommendations[0][0]['title']} by {recommendations[0][0]['artist']}" if recommendations else None,
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            logger.error(f"Test {test_name} failed with error: {e}")
            result = {
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e)
            }
            self.results.append(result)
            return result
    
    def print_summary(self) -> None:
        """Print a summary of all test results."""
        if not self.results:
            print("No tests run yet.")
            return
        
        print("\n" + "="*100)
        print("VIBEFINDER RELIABILITY TEST SUMMARY")
        print("="*100)
        
        passed = sum(1 for r in self.results if r.get("status") == "PASS")
        failed = sum(1 for r in self.results if r.get("status") == "FAIL")
        
        print(f"\nOverall Results: {passed}/{len(self.results)} tests passed\n")
        
        for result in self.results:
            status_icon = "✓" if result.get("status") == "PASS" else "✗"
            print(f"{status_icon} {result.get('test_name')}")
            
            if result.get("status") == "PASS":
                print(f"    Top recommendation: {result.get('top_recommendation')}")
                print(f"    Avg confidence: {result.get('avg_confidence')} (min: {result.get('min_confidence')}, max: {result.get('max_confidence')})")
                print(f"    Avg score: {result.get('avg_score')}")
                
                if result.get("expected_genres"):
                    match_rate = result.get("genre_match_rate")
                    print(f"    Genre match: {result.get('genre_match_count')}/{len(result.get('expected_genres'))} ({match_rate*100:.0f}%)")
                
                if result.get("used_llm") and result.get("used_llm") > 0:
                    print(f"    LLM explanations: {result.get('used_llm')}/{result.get('num_recommendations')} used")
            else:
                print(f"    Error: {result.get('error')}")
            
            print()
        
        # Statistics
        all_confidences = [r.get("avg_confidence") for r in self.results if r.get("status") == "PASS" and r.get("avg_confidence")]
        if all_confidences:
            avg_conf = round(sum(all_confidences) / len(all_confidences), 2)
            print(f"Overall average confidence across all tests: {avg_conf}")
        
        print("="*100 + "\n")
    
    def save_results(self, output_file: str = "test_results.json") -> None:
        """Save test results to JSON file."""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Test results saved to {output_file}")


def run_standard_evaluation(songs_csv: str = "data/songs.csv", use_llm: bool = False) -> None:
    """Run the standard evaluation suite for VibeFinder."""
    
    evaluator = RecommendationEvaluator(songs_csv)
    
    # Test 1: High-Energy Pop
    evaluator.run_test_case(
        "High-Energy Pop Profile",
        {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.90,
            "likes_acoustic": False,
            "preferred_mood_tag": "bright",
            "preferred_decade": 2020,
            "target_popularity": 85,
            "likes_instrumental": False,
            "target_focus": 0.40,
            "mode": "genre-first",
        },
        expected_genres=["pop", "edm", "indie pop"],
        use_llm=use_llm,
        k=5
    )
    
    # Test 2: Chill Lofi
    evaluator.run_test_case(
        "Chill Lofi Profile",
        {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.35,
            "likes_acoustic": True,
            "preferred_mood_tag": "calm",
            "preferred_decade": 2020,
            "target_popularity": 60,
            "likes_instrumental": True,
            "target_focus": 0.80,
            "mode": "mood-first",
        },
        expected_genres=["lofi", "ambient", "jazz"],
        use_llm=use_llm,
        k=5
    )
    
    # Test 3: Deep Intense Rock
    evaluator.run_test_case(
        "Deep Intense Rock Profile",
        {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.85,
            "likes_acoustic": False,
            "preferred_mood_tag": "dark",
            "preferred_decade": 2010,
            "target_popularity": 70,
            "likes_instrumental": False,
            "target_focus": 0.50,
            "mode": "energy-focused",
        },
        expected_genres=["rock", "metal"],
        use_llm=use_llm,
        k=5
    )
    
    # Test 4: Acoustic but Intense (edge case)
    evaluator.run_test_case(
        "Acoustic Intense Profile (Edge Case)",
        {
            "genre": "indie pop",
            "mood": "intense",
            "energy": 0.75,
            "likes_acoustic": True,
            "preferred_mood_tag": "dramatic",
            "preferred_decade": 2015,
            "target_popularity": 75,
            "likes_instrumental": False,
            "target_focus": 0.60,
            "mode": "balanced",
        },
        expected_genres=["indie pop", "acoustic"],
        use_llm=use_llm,
        k=5
    )
    
    # Test 5: Instrumental Jazz Focus
    evaluator.run_test_case(
        "Instrumental Jazz Profile",
        {
            "genre": "jazz",
            "mood": "sophisticated",
            "energy": 0.50,
            "likes_acoustic": True,
            "preferred_mood_tag": "sophisticated",
            "preferred_decade": 2000,
            "target_popularity": 65,
            "likes_instrumental": True,
            "target_focus": 0.70,
            "mode": "balanced",
        },
        expected_genres=["jazz", "classical"],
        use_llm=use_llm,
        k=5
    )
    
    # Print and save results
    evaluator.print_summary()
    evaluator.save_results()


if __name__ == "__main__":
    use_llm = "--llm" in sys.argv
    run_standard_evaluation(use_llm=use_llm)
