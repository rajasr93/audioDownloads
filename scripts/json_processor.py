#!/usr/bin/env python3
import re
import json
import os
from typing import List, Dict

class PlaylistProcessor:
    """Processes playlist text files and converts them to JSON format."""
    
    def __init__(self, input_file: str, output_file: str):
        self.input_file = input_file
        self.output_file = output_file
        
    def _clean_song_name(self, song: str) -> str:
        """Cleans the song name by removing timestamps and ID entries."""
        # Remove timestamps (XX:XX)
        song = re.sub(r'[\[\]\(\)\{\}]', '', song)
        song = re.sub(r'^\d{1,2}:?\d{2}:?\d{2}\s*', '', song)
        song = re.sub(r'^\d{1,2}:?\d{2}\s*', '', song)
        
        
        # Remove ID entries
        if song.strip() == "ID - ID":
            return ""
        
        return song.strip()
    
    def process_playlist(self) -> List[str]:
        """Processes the playlist file and returns a list of clean song names."""
        songs = []
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            for line in f:
                clean_song = self._clean_song_name(line)
                if clean_song:  # Only add non-empty songs
                    songs.append(clean_song)
        
        return songs
    
    def save_to_json(self, songs: List[str]) -> None:
        """Saves the processed songs to a JSON file."""
        song_dict = {"songs": [{"name": song, "youtube_id": ""} for song in songs]}
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(song_dict, f, indent=2, ensure_ascii=False)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Process playlist text file to JSON')
    parser.add_argument('-i', '--input', type=str, default='../tracklist.txt',
                        help='Input playlist text file path')
    parser.add_argument('-o', '--output', type=str, default='songs.json',
                        help='Output JSON file path')
    args = parser.parse_args()
    
    input_file = args.input
    output_file = args.output
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return
    
    processor = PlaylistProcessor(input_file, output_file)
    songs = processor.process_playlist()
    processor.save_to_json(songs)
    print(f"Successfully processed {len(songs)} songs and saved to {output_file}")

if __name__ == "__main__":
    main()