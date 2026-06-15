"""Crawl tracks and metadata from the authenticated user's Spotify profile."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import settings
from src.data_collection.auth import SpotifyAuth
from src.data_collection.crawler import SpotifyCrawler
from src.data_collection.profile_client import SpotifyProfileClient
from src.data_collection.profile_crawler import SpotifyProfileCrawler
from src.preprocessing.pipeline import PreprocessingPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Crawl tracks from your Spotify profile (liked songs + playlists)"
    )
    parser.add_argument(
        "--target",
        type=int,
        default=10_000,
        help="Target number of unique tracks (default: 10000)",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=500,
        help="Save progress every N new tracks (default: 500)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing raw/profile CSV checkpoint",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Delete existing checkpoint and start over",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not settings.spotify_client_id or not settings.spotify_client_secret:
        print("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env")
        sys.exit(1)

    raw_path = settings.raw_data_dir / "spotify_profile_tracks.csv"
    state_path = settings.raw_data_dir / "spotify_profile_state.json"
    if args.fresh and raw_path.exists():
        raw_path.unlink()
        print(f"Removed existing checkpoint: {raw_path}")
    if args.fresh and state_path.exists():
        state_path.unlink()
        print(f"Removed existing state: {state_path}")

    print("Connecting to Spotify (user OAuth — browser login may open)...")
    print(f"Redirect URI: {settings.spotify_redirect_uri}")
    auth = SpotifyAuth()
    spotify = auth.get_user_client()
    profile_client = SpotifyProfileClient(spotify)
    crawler = SpotifyProfileCrawler(profile_client)

    print(f"Crawling profile (target: {args.target} unique tracks)...")
    raw_df = crawler.crawl_profile(
        target_tracks=args.target,
        checkpoint_every=args.checkpoint_every,
    )

    if raw_df.empty:
        print("Error: no tracks collected. Complete OAuth login and try again.")
        sys.exit(1)

    print(f"\nCollected {len(raw_df)} unique tracks")
    if crawler.rate_limited:
        print("Stopped due to Spotify rate limit — partial data saved.")
    if "source_type" in raw_df.columns:
        print("\nTracks by source:")
        print(raw_df["source_type"].value_counts().to_string())

    print("\nRunning preprocessing pipeline...")
    pipeline = PreprocessingPipeline()
    processed_df = pipeline.run(raw_df)
    processed_path = pipeline.save(processed_df, "spotify_profile_tracks.csv")
    print(f"Saved processed data: {processed_path} ({len(processed_df)} tracks)")
    print("\nDone.")


if __name__ == "__main__":
    main()
