import streamlit as st


def render_track_card(track: dict, index: int) -> None:
    name = track.get("track_name", "Unknown")
    artists = track.get("artists", "Unknown")
    popularity = track.get("popularity")
    url = track.get("spotify_url")

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**{index}. {name}**")
        st.caption(artists)
    with col2:
        if popularity is not None:
            st.metric("Pop", int(popularity))
    if url:
        st.link_button("Mở Spotify", url)
    st.divider()
