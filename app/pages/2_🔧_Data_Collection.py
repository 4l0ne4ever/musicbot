import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import settings
from src.data_collection.auth import SpotifyAuth
from src.data_collection.client import SpotifyClient
from src.data_collection.crawler import SpotifyCrawler
from src.preprocessing.pipeline import PreprocessingPipeline

st.set_page_config(page_title="Data Collection", page_icon="🔧", layout="wide")
st.title("🔧 Thu thập dữ liệu từ Spotify")

if not settings.spotify_client_id or not settings.spotify_client_secret:
    st.error("Thiếu Spotify credentials trong file `.env`.")
    st.stop()

st.markdown(
    f"Redirect URI: `{settings.spotify_redirect_uri}` — "
    "đảm bảo đã cấu hình trong Spotify Developer Dashboard."
)

queries_text = st.text_area(
    "Danh sách từ khóa tìm kiếm (mỗi dòng một từ khóa)",
    value="happy vibes\nsad songs\nchill music\nworkout playlist\nromantic songs",
    height=150,
)
limit = st.slider("Số bài hát mỗi từ khóa", min_value=10, max_value=50, value=30)

if st.button("Bắt đầu thu thập", type="primary"):
    queries = [q.strip() for q in queries_text.splitlines() if q.strip()]
    if not queries:
        st.warning("Vui lòng nhập ít nhất một từ khóa.")
        st.stop()

    with st.spinner("Đang thu thập dữ liệu từ Spotify..."):
        try:
            auth = SpotifyAuth()
            client = SpotifyClient(auth.get_app_client())
            crawler = SpotifyCrawler(client)

            raw_df = crawler.crawl_by_queries(queries, limit_per_query=limit)
            raw_df = crawler.enrich_with_audio_features(raw_df)
            raw_df = crawler.enrich_with_genres(raw_df)
            raw_path = crawler.save_raw(raw_df, "spotify_tracks.csv")

            pipeline = PreprocessingPipeline()
            processed_df = pipeline.run(raw_df)
            processed_path = pipeline.save(processed_df, "spotify_tracks.csv")

            st.success(
                f"Thu thập xong **{len(processed_df)}** bài hát.\n\n"
                f"- Raw: `{raw_path}`\n"
                f"- Processed: `{processed_path}`"
            )
            st.dataframe(processed_df.head(20), use_container_width=True)
        except Exception as exc:
            st.error(f"Lỗi khi thu thập: {exc}")
