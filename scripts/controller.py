#!/usr/bin/env python3
import argparse
import os
from json_processor import PlaylistProcessor
from youtube_searcher import YouTubeSearcher
from main import DownloadManager
import json

def create_song_json(song_name: str, output_file: str = "temp_songs.json") -> bool:
    """Create a temporary JSON file for single song"""
    try:
        song_data = {
            "songs": [
                {
                    "name": song_name,
                    "youtube_id": ""
                }
            ]
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(song_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error creating song JSON: {e}")
        return False

def process_single_song(song_name: str, download_dir: str = "downloads") -> bool:
    """Pipeline for downloading a single song"""
    temp_json = "temp_songs.json"
    try:
        # Create JSON for single song
        if not create_song_json(song_name, temp_json):
            return False

        # Search YouTube
        searcher = YouTubeSearcher(temp_json, max_threads=1)
        searcher.update_json_with_ids()

        # Download song
        manager = DownloadManager(temp_json, download_dir)
        manager.download_songs()

        return True

    except Exception as e:
        print(f"Error processing song: {e}")
        return False
    finally:
        # Cleanup temp file
        if os.path.exists(temp_json):
            os.remove(temp_json)

def process_playlist(playlist_path: str, output_json: str = "songs.json", 
                    download_dir: str = "downloads", threads: int = 3) -> bool:
    """Pipeline for processing a playlist file"""
    try:
        # Process playlist to JSON
        processor = PlaylistProcessor(playlist_path, output_json)
        songs = processor.process_playlist()
        processor.save_to_json(songs)
        print(f"Processed {len(songs)} songs from playlist")

        # Search YouTube
        searcher = YouTubeSearcher(output_json, max_threads=threads)
        searcher.update_json_with_ids()

        # Download songs
        manager = DownloadManager(output_json, download_dir)
        manager.download_songs()

        return True

    except Exception as e:
        print(f"Error processing playlist: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="YouTube Music Downloader Controller")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--playlist', help='Path to playlist file')
    group.add_argument('-s', '--song', help='Single song to download')
    
    parser.add_argument('-o', '--output', default='songs.json',
                      help='Output JSON file (for playlist only)')
    parser.add_argument('-d', '--dir', default='downloads',
                      help='Download directory')
    parser.add_argument('-t', '--threads', type=int, default=3,
                      help='Number of search threads (for playlist only)')

    args = parser.parse_args()

    # Create download directory if it doesn't exist
    os.makedirs(args.dir, exist_ok=True)

    if args.song:
        print(f"Processing single song: {args.song}")
        success = process_single_song(args.song, args.dir)
    else:
        print(f"Processing playlist: {args.playlist}")
        success = process_playlist(args.playlist, args.output, args.dir, args.threads)

    if success:
        print("Processing completed successfully!")
    else:
        print("Processing failed!")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())