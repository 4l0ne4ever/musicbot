import json
from pathlib import Path

import pandas as pd

from config.settings import settings
from src.preprocessing.metadata import normalize_metadata
from src.preprocessing.mood_inferrer import fill_missing_mood_labels
from src.preprocessing.text_cleaner import TextCleaner
from src.preprocessing.text_processor import TextProcessor


class PreprocessingPipeline:
    INPUT_FILE = "spotify_hybrid_tracks.csv"
    OUTPUT_FILE = "spotify_hybrid_processed.csv"
    SUMMARY_FILE = "processing_summary.json"

    def __init__(self) -> None:
        self.text_cleaner = TextCleaner()
        self.text_processor = TextProcessor()

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        processed = df.copy()
        initial_rows = len(processed)

        processed = processed.drop_duplicates(subset=["track_id"], keep="first")
        processed = processed.dropna(subset=["track_name", "artists"])

        if "track_name" in processed.columns:
            processed["track_name_clean"] = processed["track_name"].apply(
                self.text_cleaner.clean
            )
        if "artists" in processed.columns:
            processed["artists_clean"] = processed["artists"].apply(
                self.text_cleaner.clean
            )

        processed, inferred_count = fill_missing_mood_labels(processed)
        processed = normalize_metadata(processed)

        text_cols = processed.apply(
            lambda row: pd.Series(self.text_processor.process_row(row.to_dict())),
            axis=1,
        )
        processed = pd.concat([processed, text_cols], axis=1)

        processed = self._handle_missing_values(processed)

        self._last_summary = {
            "initial_rows": initial_rows,
            "final_rows": len(processed),
            "duplicates_removed": initial_rows - len(processed),
            "mood_labels_inferred": inferred_count,
            "mood_distribution": processed["mood_label"].value_counts().to_dict(),
            "missing_after_processing": {
                col: int(processed[col].isna().sum())
                for col in processed.columns
                if processed[col].isna().any()
            },
        }
        return processed

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()

        text_defaults = {
            "tags": "",
            "tags_normalized": "",
            "search_query": "",
            "combined_text": "",
            "tokens": "",
        }
        for col, default in text_defaults.items():
            if col in out.columns:
                out[col] = out[col].fillna(default)

        if "token_count" in out.columns:
            out["token_count"] = out["token_count"].fillna(0).astype(int)

        if "data_origin" in out.columns:
            out["data_origin"] = out["data_origin"].fillna("unknown")

        return out

    def save(self, df: pd.DataFrame, filename: str | None = None) -> Path:
        filename = filename or self.OUTPUT_FILE
        settings.processed_data_dir.mkdir(parents=True, exist_ok=True)
        output_path = settings.processed_data_dir / filename
        df.to_csv(output_path, index=False)
        return output_path

    def save_summary(self, path: Path | None = None) -> Path:
        settings.processed_data_dir.mkdir(parents=True, exist_ok=True)
        output_path = path or (settings.processed_data_dir / self.SUMMARY_FILE)
        summary = getattr(self, "_last_summary", {})
        output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return output_path

    def load(self, filename: str | None = None) -> pd.DataFrame:
        filename = filename or self.INPUT_FILE
        return pd.read_csv(settings.processed_data_dir / filename)
