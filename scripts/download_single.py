#!/usr/bin/env python3
import os
from typing import Tuple, List
from yt_dlp import YoutubeDL, postprocessor
from urllib.parse import urlparse, parse_qs
from mutagen.id3 import ID3, WOAR, error
import unittest


class FilePathCollector(postprocessor.common.PostProcessor):
    """Collects file paths during YouTube download processing."""
    
    def __init__(self):
        super(FilePathCollector, self).__init__(None)
        self.file_paths = []

    def run(self, information):
        self.file_paths.append(information['filepath'])
        return [], information


class YouTubeDownloader:
    """Handles downloading and processing of YouTube videos."""
    
    def __init__(self, output_directory: str = None, output_template: str = None):
        self.output_directory = output_directory or os.getcwd()
        self.output_template = output_template
    
    def _get_ytdl_options(self) -> dict:
        """Returns the options for yt-dlp."""
        options = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "0",
            }],
            "geo_bypass": True,
            "quiet": True,
            "external_downloader_args": ["-loglevel", "panic"]
        }
        
        # Use custom output template if provided, otherwise use default
        if self.output_template:
            options["outtmpl"] = self.output_template
        else:
            options["outtmpl"] = f"{self.output_directory}/%(id)s.%(ext)s"
        
        return options

    @staticmethod
    def _get_url_path(url: str) -> str:
        """Extracts video ID from youtu.be URLs."""
        return urlparse(url).path.rpartition('/')[2]

    @staticmethod
    def _get_url_parameter(url: str, param: str) -> str:
        """Extracts parameters from YouTube URLs."""
        return parse_qs(urlparse(url).query)[param][0]

    def _generate_metadata(self, file_path: str, link: str) -> None:
        """Adds metadata to the downloaded MP3 file."""
        try:
            tags = ID3(file_path)
            tags.add(WOAR(encoding=3, url=link))
            tags.save(v2_version=3)
        except error as e:
            print(f"Error adding metadata: {e}")

    def get_video_id(self, url: str) -> str:
        """Extracts video ID from different YouTube URL formats."""
        if "youtu.be" in url:
            return self._get_url_path(url)
        return self._get_url_parameter(url, "v")

    def download_video(self, video_id: str) -> Tuple[int, str]:
        """Downloads a video and returns the result and file path."""
        link = f"https://www.youtube.com/watch?v={video_id}"
        
        with YoutubeDL(self._get_ytdl_options()) as ytdl:
            file_path_collector = FilePathCollector()
            ytdl.add_post_processor(file_path_collector)
            result = ytdl.download([link])
            
            if not file_path_collector.file_paths:
                raise ValueError(f"Download failed for video ID: {video_id}")
                
            file_path = file_path_collector.file_paths[0]
            self._generate_metadata(file_path, link)
            return result, file_path

    def download_multiple_videos(self, video_ids: List[str]) -> List[Tuple[str, int, str]]:
        """Downloads multiple videos and returns their results."""
        results = []
        for video_id in video_ids:
            try:
                result, file_path = self.download_video(video_id)
                results.append((video_id, result, file_path))
            except Exception as e:
                print(f"Error downloading video {video_id}: {e}")
                results.append((video_id, -1, ""))
        return results


def main():
    """Main function to run the downloader."""
    downloader = YouTubeDownloader()
    
    # Accept multiple video IDs
    print("Enter YouTube video IDs (one per line, empty line to finish):")
    video_ids = []
    while True:
        video_id = input().strip()
        if not video_id:
            break
        video_ids.append(video_id)
    
    if not video_ids:
        print("No video IDs provided.")
        return
    
    results = downloader.download_multiple_videos(video_ids)
    
    # Print results
    print("\nDownload Results:")
    for video_id, result, file_path in results:
        status = "Success" if result == 0 and file_path else "Failed"
        print(f"Video ID: {video_id} - Status: {status}")
        if file_path:
            print(f"Saved to: {file_path}")
        print("-" * 50)


class TestYouTubeDownloader(unittest.TestCase):
    """Test cases for YouTubeDownloader class."""
    
    def setUp(self):
        self.downloader = YouTubeDownloader()

    def test_get_video_id_youtu_be(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        self.assertEqual(self.downloader.get_video_id(url), "dQw4w9WgXcQ")

    def test_get_video_id_youtube_com(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertEqual(self.downloader.get_video_id(url), "dQw4w9WgXcQ")

    def test_get_video_id_with_additional_params(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=123"
        self.assertEqual(self.downloader.get_video_id(url), "dQw4w9WgXcQ")


if __name__ == "__main__":
    main()
