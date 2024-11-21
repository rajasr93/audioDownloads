# YouTube Music Downloader PowerShell Script
param(
    [Parameter()][Alias('p')][string]$playlist,
    [Parameter()][Alias('s')][string]$song,
    [Parameter()][Alias('h')][switch]$help,
    [Parameter()][Alias('o')][string]$output = "songs.json",
    [Parameter()][Alias('d')][string]$downloadDir = "downloads",
    [Parameter()][Alias('t')][int]$threads = 3
)

# Function to display help message
function Show-Help {
    Write-Host "YouTube Music Downloader - Usage:" -ForegroundColor Cyan
    Write-Host "-------------------------------------"
    Write-Host ".\youtube_downloader.ps1 -p <playlist_file_path>  : Process a playlist file"
    Write-Host ".\youtube_downloader.ps1 -s `"song_name`"          : Download a single song"
    Write-Host ".\youtube_downloader.ps1 -h                       : Show this help message"
    Write-Host ".\youtube_downloader.ps1 -o <output_json>        : Specify output JSON file (default: songs.json)"
    Write-Host ".\youtube_downloader.ps1 -d <download_dir>       : Specify download directory (default: downloads)"
    Write-Host ".\youtube_downloader.ps1 -t <threads>            : Number of search threads (default: 3)"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host ".\youtube_downloader.ps1 -p C:\path\to\tracks.txt"
    Write-Host ".\youtube_downloader.ps1 -p C:\path\to\tracks.txt -t 5"
    Write-Host ".\youtube_downloader.ps1 -s `"Artist - Song Name`""
}

# Function to check if Python requirements are installed
function Check-Requirements {
    Write-Host "Checking requirements..." -ForegroundColor Cyan
    python -m pip install youtube-search yt-dlp mutagen | Out-Null
}

# Function to validate thread count
function Validate-ThreadCount {
    if ($threads -lt 1) {
        Write-Host "Search threads count must be at least 1. Setting to default (3)." -ForegroundColor Yellow
        $script:threads = 3
    }
    elseif ($threads -gt 10) {
        Write-Host "Warning: High thread count may cause rate limiting issues." -ForegroundColor Yellow
    }
}

# Function to process playlist
function Process-Playlist {
    param($playlistPath)
    
    if (-not (Test-Path $playlistPath)) {
        Write-Host "Error: File not found at $playlistPath" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Processing playlist from: $playlistPath" -ForegroundColor Green
    python json_processor.py -i "$playlistPath" -o "$output"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error processing playlist" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Searching for YouTube IDs using $threads threads..." -ForegroundColor Green
    python youtube_searcher.py -f "$output" -t $threads
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error searching for YouTube IDs" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Downloading songs..." -ForegroundColor Green
    
    # Create downloads directory if it doesn't exist
    if (-not (Test-Path $downloadDir)) {
        New-Item -ItemType Directory -Path $downloadDir | Out-Null
    }
    
    python main.py -f "$output" -d "$downloadDir"
    
    Write-Host "Process completed! Check the '$downloadDir' folder for your songs." -ForegroundColor Green
}

# Function to download single song
function Download-SingleSong {
    param($songName)
    
    # Create a temporary JSON file with the single song
    $jsonContent = @{
        songs = @(
            @{
                name = $songName
                youtube_id = ""
            }
        )
    } | ConvertTo-Json | Out-File -Encoding UTF8 "temp_songs.json"
    
    # Write JSON without BOM
    [System.IO.File]::WriteAllText("temp_songs.json", $jsonContent, [System.Text.UTF8Encoding]::new($false))
    
    Write-Host "Searching for YouTube ID for: $songName" -ForegroundColor Green
    python youtube_searcher.py -f "temp_songs.json" -t 1  # Single song, single thread
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error searching for song" -ForegroundColor Red
        Remove-Item "temp_songs.json" -ErrorAction SilentlyContinue
        exit 1
    }
    
    # Create downloads directory if it doesn't exist
    if (-not (Test-Path $downloadDir)) {
        New-Item -ItemType Directory -Path $downloadDir | Out-Null
    }
    
    Write-Host "Downloading song..." -ForegroundColor Green
    python main.py -f "temp_songs.json" -d "$downloadDir"
    
    # Clean up temporary file
    Remove-Item "temp_songs.json" -ErrorAction SilentlyContinue
    
    Write-Host "Download completed! Check the '$downloadDir' folder for your song." -ForegroundColor Green
}

# Check if python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed. Please install Python to continue." -ForegroundColor Red
    exit 1
}

# Initial setup
Check-Requirements
Validate-ThreadCount

# Process arguments
if ($help -or (-not $playlist -and -not $song)) {
    Show-Help
    exit 0
}

if ($playlist) {
    Process-Playlist $playlist
}
elseif ($song) {
    Download-SingleSong $song
}