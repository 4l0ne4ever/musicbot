from typing import Any

from src.mood_classification.predictor import MoodPredictor
from src.recommendation.engine import RecommendationEngine


class ChatbotHandler:
    GREETING = (
        "Xin chào! Hãy mô tả tâm trạng của bạn — ví dụ: "
        "'mình đang căng thẳng' hoặc 'muốn nghe nhạc vui'."
    )

    def __init__(
        self,
        mood_predictor: MoodPredictor,
        recommendation_engine: RecommendationEngine,
    ) -> None:
        self._mood_predictor = mood_predictor
        self._recommendation_engine = recommendation_engine

    def handle_message(self, user_message: str) -> dict[str, Any]:
        mood, confidence = self._mood_predictor.predict_from_text(user_message)
        recommendations = self._recommendation_engine.recommend_by_mood(mood, limit=10)

        reply = self._build_reply(mood, confidence, recommendations)
        return {
            "user_message": user_message,
            "detected_mood": mood,
            "confidence": confidence,
            "recommendations": recommendations,
            "reply": reply,
        }

    def _build_reply(
        self,
        mood: str,
        confidence: float,
        recommendations: list[dict[str, Any]],
    ) -> str:
        if not recommendations:
            return (
                f"Mình nhận thấy bạn đang ở trạng thái **{mood}**, "
                "nhưng chưa tìm được bài hát phù hợp. Hãy thử mô tả rõ hơn nhé!"
            )

        lines = [
            f"Mình cảm nhận bạn đang **{mood}** "
            f"(độ tin cậy: {confidence:.0%}). Đây là vài gợi ý cho bạn:",
        ]
        for i, track in enumerate(recommendations[:5], start=1):
            lines.append(
                f"{i}. **{track.get('track_name')}** — {track.get('artists')}"
            )
        return "\n".join(lines)
