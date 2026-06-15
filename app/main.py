import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.components.chat_ui import render_chat_history
from config.settings import settings
from src.chatbot.handler import ChatbotHandler
from src.data_collection.auth import SpotifyAuth
from src.data_collection.client import SpotifyClient
from src.mood_classification.predictor import MoodPredictor
from src.recommendation.engine import RecommendationEngine

st.set_page_config(
    page_title="Mood Music Chatbot",
    page_icon="🎵",
    layout="wide",
)


@st.cache_resource
def get_chatbot() -> ChatbotHandler:
    auth = SpotifyAuth()
    spotify = auth.get_user_client()
    client = SpotifyClient(spotify)
    engine = RecommendationEngine(client)
    return ChatbotHandler(MoodPredictor(), engine)


def main() -> None:
    st.title("🎵 Mood-based Music Recommendation Chatbot")
    st.caption("Gợi ý nhạc theo tâm trạng — dữ liệu từ Spotify API")

    if not settings.spotify_client_id or not settings.spotify_client_secret:
        st.error("Thiếu Spotify credentials trong file `.env`.")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": ChatbotHandler.GREETING}
        ]

    render_chat_history(st.session_state.messages)

    if prompt := st.chat_input("Mô tả tâm trạng của bạn..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Đang phân tích tâm trạng và tìm bài hát..."):
            try:
                chatbot = get_chatbot()
                result = chatbot.handle_message(prompt)
                assistant_msg = {
                    "role": "assistant",
                    "content": result["reply"],
                    "recommendations": result["recommendations"],
                }
            except Exception as exc:
                assistant_msg = {
                    "role": "assistant",
                    "content": (
                        f"Không thể kết nối Spotify API. "
                        f"Hãy đảm bảo đã đăng nhập OAuth. Chi tiết: {exc}"
                    ),
                }

        st.session_state.messages.append(assistant_msg)
        st.rerun()


if __name__ == "__main__":
    main()
