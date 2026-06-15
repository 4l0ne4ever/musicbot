from src.mood_classification.labels import MOOD_KEYWORDS, MOOD_LABELS


class MoodPredictor:
    def predict_from_text(self, text: str) -> tuple[str, float]:
        text_lower = text.lower()
        scores = {
            mood: sum(1 for kw in keywords if kw in text_lower)
            for mood, keywords in MOOD_KEYWORDS.items()
        }
        best_mood = max(scores, key=scores.get)
        total = sum(scores.values()) or 1
        confidence = scores[best_mood] / total
        if scores[best_mood] == 0:
            return "calm", 0.0
        return best_mood, confidence

    @property
    def labels(self) -> list[str]:
        return MOOD_LABELS.copy()
