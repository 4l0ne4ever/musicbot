import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import settings
from src.analysis.eda import EDAAnalyzer

st.set_page_config(page_title="Data Explorer", page_icon="📊", layout="wide")
st.title("📊 Data Explorer")

processed_files = list(settings.processed_data_dir.glob("*.csv"))
if not processed_files:
    st.info("Chưa có dữ liệu đã xử lý. Hãy chạy pipeline thu thập dữ liệu trước.")
    st.stop()

selected = st.selectbox("Chọn file dữ liệu", processed_files)
df = __import__("pandas").read_csv(selected)
analyzer = EDAAnalyzer(df)

summary = analyzer.summary()
col1, col2, col3 = st.columns(3)
col1.metric("Tổng bài hát", summary["total_tracks"])
col2.metric("Nghệ sĩ", summary["unique_artists"])
if summary["avg_popularity"] is not None:
    col3.metric("Popularity TB", f"{summary['avg_popularity']:.1f}")

fig_pop = analyzer.popularity_histogram()
if fig_pop:
    st.plotly_chart(fig_pop, use_container_width=True)

fig_artists = analyzer.top_artists_chart()
if fig_artists:
    st.plotly_chart(fig_artists, use_container_width=True)

st.dataframe(df.head(100), use_container_width=True)
