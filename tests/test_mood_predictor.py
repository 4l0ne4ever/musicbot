import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.mood_classification.predictor import MoodPredictor


def test_predict_happy():
    predictor = MoodPredictor()
    mood, _ = predictor.predict_from_text("I feel so happy and excited today")
    assert mood == "happy"


def test_predict_sad():
    predictor = MoodPredictor()
    mood, _ = predictor.predict_from_text("I am sad and lonely")
    assert mood == "sad"
