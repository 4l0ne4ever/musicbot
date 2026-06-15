import streamlit as st

from app.components.track_card import render_track_card


def render_chat_history(messages: list[dict]) -> None:
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("recommendations"):
                with st.expander("Danh sách bài hát gợi ý"):
                    for i, track in enumerate(msg["recommendations"], start=1):
                        render_track_card(track, i)
