"""Chạy pipeline tiền xử lý dữ liệu Spotify hybrid."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import settings
from src.preprocessing.pipeline import PreprocessingPipeline


def main() -> None:
    input_path = settings.processed_data_dir / PreprocessingPipeline.INPUT_FILE
    if not input_path.exists():
        print(f"Error: không tìm thấy {input_path}")
        print("Hãy chạy crawl trước hoặc đặt file spotify_hybrid_tracks.csv vào data/processed/")
        sys.exit(1)

    print(f"Loading: {input_path}")
    df = PreprocessingPipeline().load(PreprocessingPipeline.INPUT_FILE)
    print(f"Input: {len(df)} tracks, {len(df.columns)} columns")

    pipeline = PreprocessingPipeline()
    processed = pipeline.run(df)

    output_path = pipeline.save(processed)
    summary_path = pipeline.save_summary()

    summary = pipeline._last_summary
    print(f"\nSaved processed data: {output_path} ({len(processed)} tracks)")
    print(f"Saved summary: {summary_path}")
    print(f"Mood labels inferred: {summary.get('mood_labels_inferred', 0)}")
    print("\nMood distribution:")
    for mood, count in summary.get("mood_distribution", {}).items():
        print(f"  {mood}: {count}")

    print("\nDone.")


if __name__ == "__main__":
    main()
