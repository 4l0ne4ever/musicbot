import pandas as pd

MOOD_KEYWORDS: dict[str, list[str]] = {
    "happy": ["happy", "joy", "excited", "fun", "cheerful", "vui", "hạnh phúc"],
    "sad": ["sad", "lonely", "depressed", "cry", "buồn", "cô đơn"],
    "calm": ["calm", "relax", "peaceful", "chill", "thư giãn", "bình yên"],
    "energetic": ["energy", "workout", "pump", "hype", "năng lượng", "tập trung"],
    "romantic": ["love", "romantic", "date", "yêu", "lãng mạn"],
    "stressed": ["stress", "anxious", "tired", "overwhelmed", "căng thẳng", "mệt"],
}


def infer_mood_label(row: dict) -> str | None:
    text_parts = [
        str(row.get("source_name", "") or ""),
        str(row.get("search_query", "") or ""),
        str(row.get("tags", "") or ""),
        str(row.get("track_name", "") or ""),
    ]
    text = " ".join(text_parts).lower()
    if not text.strip():
        return None

    scores = {
        mood: sum(1 for kw in keywords if kw in text)
        for mood, keywords in MOOD_KEYWORDS.items()
    }
    best_mood, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score == 0:
        return None
    return best_mood


def fill_missing_mood_labels(df):
    out = df.copy()
    if "mood_label" not in out.columns:
        out["mood_label"] = None

    missing_mask = out["mood_label"].isna() | (out["mood_label"].astype(str).str.strip() == "")
    inferred_flags = pd.Series(False, index=out.index)
    inferred = 0

    for idx in out.index[missing_mask]:
        mood = infer_mood_label(out.loc[idx].to_dict())
        if mood:
            out.at[idx, "mood_label"] = mood
            inferred_flags.at[idx] = True
            inferred += 1

    still_missing = out["mood_label"].isna() | (out["mood_label"].astype(str).str.strip() == "")
    out.loc[still_missing, "mood_label"] = "calm"

    out["mood_inferred"] = inferred_flags
    return out, inferred
