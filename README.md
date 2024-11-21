# YouTube Music Downloader

A PowerShell script to easily download music from YouTube playlists or single songs with proper metadata and organization.

## Features

- Download entire playlists from YouTube
- Download single songs
- Multithreaded YouTube search capability
- Automatic metadata handling
- Configurable output directories
- WAV format audio extraction

## Prerequisites

1. **Python 3.x**
   - Download and install from [Python.org](https://www.python.org/downloads/)
   - Ensure Python is added to PATH during installation

2. **Required Python Packages**
   - The script will automatically install these packages:
     - youtube-search
     - yt-dlp
     - mutagen

3. **PowerShell**
   - Windows PowerShell or PowerShell Core

## Installation

1. Clone or download this repository
2. Ensure all Python scripts are in the same directory as the PowerShell script:
   - `youtube_downloader.ps1` (Main PowerShell script)
   - `json_processor.py`
   - `youtube_searcher.py`
   - `main.py`

## Usage

### Basic Commands

1. **Download Single Song**
```powershell
.\youtube_downloader.ps1 -s "Artist Name - Song Name"
```

2. **Process Playlist from Text File**
```powershell
.\youtube_downloader.ps1 -p "path/to/playlist.txt"
```

3. **Show Help**
```powershell
.\youtube_downloader.ps1 -h
```

### Advanced Options

```powershell
# Specify output JSON file
.\youtube_downloader.ps1 -p "playlist.txt" -o "custom_output.json"

# Specify download directory
.\youtube_downloader.ps1 -p "playlist.txt" -d "my_music"

# Set number of search threads (default: 3)
.\youtube_downloader.ps1 -p "playlist.txt" -t 5
```

### Playlist File Format

The playlist text file should contain one song per line:
```
Artist1 - Song1
Artist2 - Song2
Artist3 - Song3
```

## Directory Structure

```
youtube_downloader/
├── youtube_downloader.ps1
├── json_processor.py
├── youtube_searcher.py
├── main.py
├── downloads/          # Default download directory
│   └── songs...
└── songs.json         # Generated JSON file
```

## Configuration

- Default download directory: `./downloads`
- Default JSON output: `songs.json`
- Default thread count: 3
- Maximum recommended threads: 10

## Troubleshooting

1. **PowerShell Execution Policy**
   If you get execution policy errors, run PowerShell as Administrator and execute:
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Python Not Found**
   Ensure Python is added to PATH during installation or add it manually

3. **Permission Issues**
   - Run PowerShell as Administrator if having permission issues
   - Ensure write access to the download directory

4. **Download Errors**
   - Check your internet connection
   - Verify the song name is correct
   - Try reducing thread count if getting rate limited

## Notes

- The script downloads audio in WAV format for best quality
- Songs are downloaded one by one to prevent rate limiting
- Thread count affects only the YouTube search process, not downloads
- Temporary files are automatically cleaned up after downloads

## Known Limitations

- YouTube search might not always find the exact version of a song
- Rate limiting might occur with high thread counts
- Some antivirus software might block FFmpeg operations

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.