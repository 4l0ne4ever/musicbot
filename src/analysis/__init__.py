from src.analysis.visualize import DataVisualizer

__all__ = ["DataVisualizer", "EDAAnalyzer"]


def __getattr__(name: str):
    if name == "EDAAnalyzer":
        from src.analysis.eda import EDAAnalyzer
        return EDAAnalyzer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
