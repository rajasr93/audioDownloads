#!/usr/bin/env python3
import json
import os
import re
from typing import List, Dict
from download_single import YouTubeDownloader

class DownloadManager:
    """Manages the downloading of songs from YouTube."""
    
    def __init__(self, json_file: str, download_dir: str):
        self.json_file = json_file
        self.download_dir = download_dir
        self.ensure_download_directory()
    
    def ensure_download_directory(self) -> None:
        """Creates the download directory if it doesn't exist."""
        os.makedirs(self.download_dir, exist_ok=True)
    
    def load_songs(self) -> List[Dict[str, str]]:
        """Loads songs from the JSON file."""
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['songs']
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitizes the filename by removing invalid characters and limiting length.
        """
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace multiple spaces with single space
        filename = re.sub(r'\s+', ' ', filename)
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        # Limit length (Windows has 255 char limit, leaving room for extension)
        if len(filename) > 250:
            filename = filename[:250]
        return filename
    
    def _get_safe_filename(self, song_name: str, youtube_id: str) -> str:
        """
        Creates a safe filename using song name and youtube_id as fallback.
        """
        base_name = self._sanitize_filename(song_name)
        if not base_name:
            base_name = youtube_id
        return f"{base_name}"
    
    def _get_output_template(self, song_name: str, youtube_id: str) -> str:
        """
        Creates the output template for yt-dlp.
        """
        filename = self._get_safe_filename(song_name, youtube_id)
        return os.path.join(self.download_dir, filename)
    
    def download_songs(self) -> None:
        """Downloads all songs from the JSON file."""
        songs = self.load_songs()
        
        for song in songs:
            if song['youtube_id']:
                try:
                    print(f"Downloading: {song['name']}")
                    output_template = self._get_output_template(song['name'], song['youtube_id'])
                    
                    # Create custom downloader for each song with specific output template
                    downloader = YouTubeDownloader(self.download_dir, output_template)
                    
                    result, file_path = downloader.download_video(song['youtube_id'])
                    if result == 0:
                        print(f"Successfully downloaded: {song['name']}")
                        print(f"Saved as: {os.path.basename(file_path)}")
                    else:
                        print(f"Failed to download: {song['name']}")
                except Exception as e:
                    print(f"Error downloading {song['name']}: {e}")
            else:
                print(f"No YouTube ID found for: {song['name']}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Download songs from YouTube using JSON file')
    parser.add_argument('-f', '--file', type=str, default='songs.json',
                        help='Input JSON file path (default: songs.json)')
    parser.add_argument('-d', '--dir', type=str, default='downloads',
                        help='Download directory (default: downloads)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: {args.file} not found!")
        return
    
    manager = DownloadManager(args.file, args.dir)
    manager.download_songs()

if __name__ == "__main__":
    main()