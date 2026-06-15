import re
import string


class TextCleaner:
    def __init__(self, lowercase: bool = True, remove_punctuation: bool = True) -> None:
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation

    def clean(self, text: str) -> str:
        if not isinstance(text, str):
            return ""

        cleaned = text.strip()
        if self.lowercase:
            cleaned = cleaned.lower()
        if self.remove_punctuation:
            cleaned = cleaned.translate(str.maketrans("", "", string.punctuation))
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()
