#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
import os
from controller import process_single_song, process_playlist, create_song_json
from werkzeug.utils import secure_filename
from queue import Queue
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def save_tracklist(content, filename):
    """Save tracklist content to a file"""
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download_song', methods=['POST'])
def download_song():
    try:
        data = request.get_json()  # Changed from request.form
        song_name = data.get('song_name')
        download_dir = data.get('download_dir', 'downloads')
        
        if not song_name:
            return jsonify({'success': False, 'error': 'Song name is required'})
        
        success = process_single_song(song_name, download_dir)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download_tracklist', methods=['POST'])
def download_tracklist():
    try:
        data = request.get_json()  # Changed from request.form
        tracklist = data.get('tracklist')
        download_dir = data.get('download_dir', 'downloads')
        
        if not tracklist:
            return jsonify({'success': False, 'error': 'Tracklist is required'})
        
        # Save tracklist to file
        tracklist_file = save_tracklist(tracklist, 'tracklist.txt')
        
        try:
            success = process_playlist(tracklist_file, 'songs.json', download_dir)
            return jsonify({'success': success})
        finally:
            # Cleanup tracklist file
            if os.path.exists(tracklist_file):
                os.remove(tracklist_file)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download_playlist', methods=['POST'])
def download_playlist():
    playlist_url = request.form.get('playlist_url')
    download_dir = request.form.get('download_dir', 'downloads')
    
    if not playlist_url:
        return jsonify({'success': False, 'error': 'Playlist URL is required'})
    
    # Here you'll need to implement the playlist URL processing
    # For now, return not implemented
    return jsonify({'success': False, 'error': 'Playlist URL download not implemented yet'})

if __name__ == '__main__':
    app.run(debug=True)