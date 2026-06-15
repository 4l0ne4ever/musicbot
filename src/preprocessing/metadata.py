import pandas as pd


def normalize_metadata(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    if "artists" in out.columns:
        out["primary_artist"] = out["artists"].apply(_first_artist)

    if "release_date" in out.columns:
        out["release_year"] = pd.to_datetime(
            out["release_date"], errors="coerce"
        ).dt.year

    if "duration_ms" in out.columns:
        out["duration_min"] = (out["duration_ms"] / 60_000).round(2)

    if "explicit" in out.columns:
        out["explicit"] = out["explicit"].fillna(False).astype(bool)

    if "tags" in out.columns:
        out["tags_list"] = out["tags"].apply(_split_tags)
        out["tags_normalized"] = out["tags_list"].apply(
            lambda parts: ", ".join(parts) if parts else ""
        )

    return out


def _first_artist(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    return value.split(",")[0].strip()


def _split_tags(value: object) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return []
    return [part.strip().lower() for part in value.split(",") if part.strip()]
