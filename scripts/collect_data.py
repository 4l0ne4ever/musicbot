"""CLI script to crawl Spotify data and run preprocessing."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import settings
from src.data_collection.auth import SpotifyAuth
from src.data_collection.client import SpotifyClient
from src.data_collection.crawler import SpotifyCrawler
from src.preprocessing.pipeline import PreprocessingPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl track data from Spotify API")
    parser.add_argument(
        "--mode",
        choices=["playlist", "track"],
        default="playlist",
        help="Crawl mode: search playlists (default) or individual tracks",
    )
    parser.add_argument(
        "--playlists-per-query",
        type=int,
        default=5,
        help="Playlists per mood query in playlist mode (default: 5)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max tracks per query in track mode (default: 50)",
    )
    parser.add_argument(
        "--skip-features",
        action="store_true",
        help="Skip audio features enrichment",
    )
    parser.add_argument(
        "--skip-genres",
        action="store_true",
        help="Skip artist genre enrichment",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not settings.spotify_client_id or not settings.spotify_client_secret:
        print("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env")
        sys.exit(1)

    auth = SpotifyAuth()
    if args.mode == "playlist":
        print("Connecting to Spotify (user OAuth)...")
        spotify = auth.get_user_client()
    else:
        print("Connecting to Spotify (client credentials)...")
        spotify = auth.get_app_client()
    client = SpotifyClient(spotify)
    crawler = SpotifyCrawler(client)

    if args.mode == "playlist":
        print(f"Crawling playlists ({args.playlists_per_query} per mood query)...")
        raw_df = crawler.crawl_by_mood_playlists(
            playlists_per_query=args.playlists_per_query
        )
    else:
        print(f"Crawling tracks ({args.limit} per mood query)...")
        raw_df = crawler.crawl_by_mood_queries(limit_per_query=args.limit)
    if raw_df.empty:
        print("Error: no tracks collected. Check API credentials and network.")
        sys.exit(1)

    if not args.skip_features:
        print("Enriching with audio features...")
        raw_df = crawler.enrich_with_audio_features(raw_df)

    if not args.skip_genres:
        print("Enriching with artist genres...")
        raw_df = crawler.enrich_with_genres(raw_df)

    raw_path = crawler.save_raw(raw_df, "spotify_tracks.csv")
    print(f"Saved raw data: {raw_path} ({len(raw_df)} tracks)")

    print("Running preprocessing pipeline...")
    pipeline = PreprocessingPipeline()
    processed_df = pipeline.run(raw_df)
    processed_path = pipeline.save(processed_df, "spotify_tracks.csv")
    print(f"Saved processed data: {processed_path} ({len(processed_df)} tracks)")

    if "mood_label" in processed_df.columns:
        print("\nTracks per mood label:")
        print(processed_df["mood_label"].value_counts().to_string())

    print("\nDone.")


if __name__ == "__main__":
    main()
