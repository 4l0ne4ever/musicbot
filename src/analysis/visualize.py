from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud

FIGURE_DPI = 120


class DataVisualizer:
    def __init__(self, df: pd.DataFrame, output_dir: Path) -> None:
        self.df = df
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_theme(style="whitegrid")

    def generate_all(self) -> list[Path]:
        saved: list[Path] = []
        saved.append(self.plot_mood_distribution())
        saved.append(self.plot_data_origin())
        saved.append(self.plot_duration_distribution())
        if "release_year" in self.df.columns and self.df["release_year"].notna().any():
            saved.append(self.plot_release_year_distribution())
        saved.append(self.plot_mood_by_origin_heatmap())
        saved.append(self.plot_top_artists_by_mood())
        saved.append(self.plot_wordcloud_by_mood())
        return [path for path in saved if path is not None]

    def plot_mood_distribution(self) -> Path:
        counts = self.df["mood_label"].value_counts().reset_index()
        counts.columns = ["mood", "count"]
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=counts, x="mood", y="count", hue="mood", palette="Set2", ax=ax, legend=False)
        ax.set_title("Phân bố bài hát theo mood")
        ax.set_xlabel("Mood")
        ax.set_ylabel("Số bài hát")
        return self._save(fig, "01_mood_distribution.png")

    def plot_data_origin(self) -> Path:
        if "data_origin" not in self.df.columns:
            return None
        counts = self.df["data_origin"].value_counts().reset_index()
        counts.columns = ["origin", "count"]
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=counts, x="origin", y="count", hue="origin", palette="pastel", ax=ax, legend=False)
        ax.set_title("Nguồn dữ liệu (profile vs search)")
        return self._save(fig, "02_data_origin.png")

    def plot_duration_distribution(self) -> Path:
        if "duration_min" not in self.df.columns:
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(self.df["duration_min"].dropna(), bins=40, kde=True, ax=ax, color="steelblue")
        ax.set_title("Phân bố độ dài bài hát (phút)")
        ax.set_xlabel("Duration (min)")
        return self._save(fig, "03_duration_distribution.png")

    def plot_release_year_distribution(self) -> Path:
        fig, ax = plt.subplots(figsize=(10, 5))
        years = self.df["release_year"].dropna().astype(int)
        sns.histplot(years, bins=30, ax=ax, color="coral")
        ax.set_title("Phân bố năm phát hành")
        ax.set_xlabel("Year")
        return self._save(fig, "04_release_year_distribution.png")

    def plot_mood_by_origin_heatmap(self) -> Path:
        if "data_origin" not in self.df.columns:
            return None
        pivot = pd.crosstab(self.df["mood_label"], self.df["data_origin"])
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(pivot, annot=True, fmt="d", cmap="YlOrRd", ax=ax)
        ax.set_title("Mood × Nguồn dữ liệu")
        return self._save(fig, "05_mood_origin_heatmap.png")

    def plot_top_artists_by_mood(self, top_n: int = 10) -> Path:
        if "primary_artist" not in self.df.columns:
            return None
        subset = (
            self.df.groupby(["mood_label", "primary_artist"])
            .size()
            .reset_index(name="count")
        )
        top = subset.sort_values("count", ascending=False).groupby("mood_label").head(top_n)
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(data=top, y="primary_artist", x="count", hue="mood_label", ax=ax)
        ax.set_title(f"Top {top_n} nghệ sĩ theo mood")
        ax.set_xlabel("Số bài")
        return self._save(fig, "06_top_artists_by_mood.png")

    def plot_wordcloud_by_mood(self) -> Path:
        if "combined_text" not in self.df.columns:
            return None
        moods = self.df["mood_label"].dropna().unique()
        n = len(moods)
        cols = 3
        rows = (n + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(15, 4 * rows))
        axes = axes.flatten() if n > 1 else [axes]

        for ax, mood in zip(axes, moods):
            text = " ".join(self.df.loc[self.df["mood_label"] == mood, "combined_text"].dropna())
            if not text.strip():
                ax.axis("off")
                continue
            cloud = WordCloud(width=800, height=400, background_color="white").generate(text)
            ax.imshow(cloud, interpolation="bilinear")
            ax.set_title(mood)
            ax.axis("off")

        for ax in axes[len(moods) :]:
            ax.axis("off")

        fig.suptitle("Word cloud theo mood (track + artist + tags)", fontsize=14)
        fig.tight_layout()
        return self._save(fig, "07_wordcloud_by_mood.png")

    def _save(self, fig: plt.Figure, filename: str) -> Path:
        path = self.output_dir / filename
        fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
        plt.close(fig)
        return path
