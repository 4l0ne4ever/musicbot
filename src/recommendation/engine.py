from typing import Any

import pandas as pd

from src.data_collection.client import SpotifyClient
from src.mood_classification.labels import MOOD_KEYWORDS


class RecommendationEngine:
    MOOD_TO_AUDIO_PARAMS: dict[str, dict[str, float]] = {
        "happy": {"target_valence": 0.8, "target_energy": 0.7, "target_danceability": 0.7},
        "sad": {"target_valence": 0.2, "target_energy": 0.3, "target_acousticness": 0.7},
        "calm": {"target_valence": 0.5, "target_energy": 0.3, "target_acousticness": 0.8},
        "energetic": {"target_valence": 0.7, "target_energy": 0.9, "target_tempo": 140},
        "romantic": {"target_valence": 0.6, "target_energy": 0.4, "target_acousticness": 0.6},
        "stressed": {"target_valence": 0.4, "target_energy": 0.2, "target_instrumentalness": 0.5},
    }

    def __init__(self, spotify_client: SpotifyClient, catalog: pd.DataFrame | None = None) -> None:
        self._client = spotify_client
        self._catalog = catalog

    def recommend_by_mood(self, mood: str, limit: int = 10) -> list[dict[str, Any]]:
        audio_params = self.MOOD_TO_AUDIO_PARAMS.get(mood, {})
        seed_genres = self._mood_seed_genres(mood)

        tracks = self._client.get_recommendations(
            seed_genres=seed_genres[:1] if seed_genres else ["pop"],
            limit=limit,
            **audio_params,
        )
        return [self._format_track(t) for t in tracks]

    def recommend_from_catalog(
        self, mood: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        if self._catalog is None or self._catalog.empty:
            return self.recommend_by_mood(mood, limit)

        keywords = MOOD_KEYWORDS.get(mood, [])
        df = self._catalog.copy()
        if keywords:
            pattern = "|".join(keywords)
            mask = df["track_name"].str.contains(pattern, case=False, na=False)
            df = df[mask] if mask.any() else df

        df = df.sort_values("popularity", ascending=False).head(limit)
        return df.to_dict(orient="records")

    @staticmethod
    def _mood_seed_genres(mood: str) -> list[str]:
        mapping = {
            "happy": ["pop", "dance"],
            "sad": ["acoustic", "indie"],
            "calm": ["ambient", "chill"],
            "energetic": ["rock", "electronic"],
            "romantic": ["r-n-b", "soul"],
            "stressed": ["classical", "ambient"],
        }
        return mapping.get(mood, ["pop"])

    @staticmethod
    def _format_track(track: dict[str, Any]) -> dict[str, Any]:
        artists = ", ".join(a["name"] for a in track.get("artists", []))
        return {
            "track_id": track.get("id"),
            "track_name": track.get("name"),
            "artists": artists,
            "popularity": track.get("popularity"),
            "spotify_url": track.get("external_urls", {}).get("spotify"),
        }
