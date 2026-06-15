from typing import Any

import pandas as pd
import plotly.express as px


class EDAAnalyzer:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def summary(self) -> dict[str, Any]:
        return {
            "total_tracks": len(self.df),
            "unique_artists": self.df["artists"].nunique() if "artists" in self.df else 0,
            "avg_popularity": (
                float(self.df["popularity"].mean())
                if "popularity" in self.df.columns
                else None
            ),
        }

    def popularity_histogram(self):
        if "popularity" not in self.df.columns:
            return None
        return px.histogram(self.df, x="popularity", nbins=30, title="Phân bố Popularity")

    def top_artists_chart(self, top_n: int = 15):
        if "artists" not in self.df.columns:
            return None
        counts = self.df["artists"].value_counts().head(top_n).reset_index()
        counts.columns = ["artist", "count"]
        return px.bar(counts, x="artist", y="count", title=f"Top {top_n} nghệ sĩ")
