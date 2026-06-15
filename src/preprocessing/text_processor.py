from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from src.preprocessing.text_cleaner import TextCleaner


class TextProcessor:
    def __init__(self) -> None:
        self._cleaner = TextCleaner()
        self._stopwords = set(ENGLISH_STOP_WORDS)

    def build_combined_text(self, row: dict) -> str:
        parts = [
            row.get("track_name_clean") or row.get("track_name", ""),
            row.get("artists_clean") or row.get("artists", ""),
            row.get("tags_normalized") or row.get("tags", ""),
            row.get("search_query", ""),
            row.get("source_name", ""),
        ]
        cleaned = [self._cleaner.clean(str(part)) for part in parts if part]
        return " ".join(part for part in cleaned if part)

    def tokenize(self, text: str) -> list[str]:
        if not text:
            return []
        tokens = text.split()
        return [token for token in tokens if token not in self._stopwords and len(token) > 1]

    def process_row(self, row: dict) -> dict:
        combined = self.build_combined_text(row)
        tokens = self.tokenize(combined)
        return {
            "combined_text": combined,
            "tokens": " ".join(tokens),
            "token_count": len(tokens),
        }
