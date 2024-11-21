#!/usr/bin/env python3
import json
import os
import time
import threading
from queue import Queue
from typing import Dict, Optional, List
from youtube_search import YoutubeSearch
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

class YouTubeSearcher:
    """Searches YouTube for songs and updates JSON with video IDs."""
    
    def __init__(self, json_file: str, max_threads: int = 3):
        self.json_file = json_file
        self.max_threads = max_threads
        self.lock = threading.Lock()
        self.rate_limit_delay = 1.0  # Delay between searches in seconds
        self.last_search_time = time.time()
    
    def _rate_limited_search(self, song_name: str) -> Optional[str]:
        """
        Performs rate-limited YouTube search.
        Uses a lock to ensure proper timing between searches across threads.
        """
        with self.lock:
            # Calculate time to wait
            current_time = time.time()
            time_since_last = current_time - self.last_search_time
            if time_since_last < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - time_since_last)
            
            try:
                results = YoutubeSearch(song_name, max_results=1).to_dict()
                self.last_search_time = time.time()
                
                if results:
                    return results[0]['id']
                return None
            except Exception as e:
                print(f"Error searching for '{song_name}': {e}")
                return None

    def _search_worker(self, song: Dict[str, str]) -> tuple[str, str, bool]:
        """
        Worker function for searching YouTube.
        Returns tuple of (song_name, video_id, success_status)
        """
        song_name = song['name']
        video_id = self._rate_limited_search(song_name)
        success = video_id is not None
        return (song_name, video_id, success)

    def update_json_with_ids(self) -> None:
        """Updates the JSON file with YouTube video IDs using parallel processing."""
        try:
            # Try reading with utf-8-sig first (handles BOM)
            with open(self.json_file, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
        except Exception as e:
            try:
                # Fallback to regular utf-8
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading JSON file: {e}")
                return
        
        # Filter songs that need YouTube IDs
        songs_to_process = [song for song in data['songs'] if not song['youtube_id']]
        
        if not songs_to_process:
            print("No songs need YouTube IDs.")
            return

        print(f"Processing {len(songs_to_process)} songs with {self.max_threads} threads...")
        songs_updated = 0
        failed_songs = []

        # Process songs in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            # Submit all songs for processing
            future_to_song = {
                executor.submit(self._search_worker, song): song
                for song in songs_to_process
            }

            # Process completed searches
            for future in as_completed(future_to_song):
                song_name, video_id, success = future.result()
                
                if success:
                    # Update the original data structure
                    for song in data['songs']:
                        if song['name'] == song_name:
                            song['youtube_id'] = video_id
                            songs_updated += 1
                            print(f"Found YouTube ID for: {song_name}")
                            break
                else:
                    failed_songs.append(song_name)

        # Save updated JSON without BOM
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print(f"\nSearch Results Summary:")
        print(f"- Successfully updated: {songs_updated} songs")
        if failed_songs:
            print(f"- Failed to find: {len(failed_songs)} songs")
            print("\nFailed songs:")
            for song in failed_songs:
                print(f"- {song}")

def main():
    parser = argparse.ArgumentParser(description='Search YouTube for songs and update JSON')
    parser.add_argument('-f', '--file', type=str, default='songs.json',
                        help='Input JSON file path')
    parser.add_argument('-t', '--threads', type=int, default=3,
                        help='Maximum number of concurrent threads (default: 3)')
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: {args.file} not found!")
        return
    
    searcher = YouTubeSearcher(args.file, max_threads=args.threads)
    searcher.update_json_with_ids()

if __name__ == "__main__":
    main()