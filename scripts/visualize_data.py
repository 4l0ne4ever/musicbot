"""Trực quan hóa dữ liệu đã xử lý."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import settings
from src.analysis.visualize import DataVisualizer
from src.preprocessing.pipeline import PreprocessingPipeline


def main() -> None:
    input_path = settings.processed_data_dir / PreprocessingPipeline.OUTPUT_FILE
    if not input_path.exists():
        print(f"Error: không tìm thấy {input_path}")
        print("Chạy trước: python scripts/process_data.py")
        sys.exit(1)

    import pandas as pd

    print(f"Loading: {input_path}")
    df = pd.read_csv(input_path)
    print(f"Visualizing {len(df)} tracks")

    figures_dir = settings.processed_data_dir / "figures"
    visualizer = DataVisualizer(df, figures_dir)
    saved = visualizer.generate_all()

    print(f"\nSaved {len(saved)} charts to {figures_dir}:")
    for path in saved:
        print(f"  - {path.name}")

    print("\nDone.")


if __name__ == "__main__":
    main()
