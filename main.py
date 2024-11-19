import pandas as pd
import random
import requests
from flask import Flask, render_template, request
from textblob import TextBlob
from config import CLIENT_ID, CLIENT_SECRET  # Import credentials from config.py

app = Flask(__name__)

# Load the Musical Sentiment Dataset from the Data folder
df = pd.read_csv('Data/musical_sentiment.csv')

import base64

def get_spotify_token():
    """Authenticate with Spotify and retrieve an access token."""
    url = 'https://accounts.spotify.com/api/token'
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
    
    headers = {'Authorization': f'Basic {auth_base64}'}
    data = {'grant_type': 'client_credentials'}
    
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()
    return response_data.get('access_token', None)

def get_spotify_preview_url(track_name, artist_name):
    """Search for a track on Spotify and return the preview URL."""
    token = get_spotify_token()
    if not token:
        print("Error: No Spotify token retrieved.")
        return None
    
    search_url = 'https://api.spotify.com/v1/search'
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'q': f'track:{track_name} artist:{artist_name}',
        'type': 'track',
        'limit': 1
    }
    
    response = requests.get(search_url, headers=headers, params=params)
    response_data = response.json()
    
    if response_data['tracks']['items']:
        return response_data['tracks']['items'][0].get('preview_url', None)
    return None

def select_songs_by_query(polarity: float, user_query: str) -> list:
    """Filters songs based on normalized polarity, genre, and emotional tags, then adds preview URLs."""
    normalized_polarity = (polarity + 1) / 2  # Normalize polarity to 0-1
    song_list = []
    used_tracks = set()  # Track already used songs

    # Filter by genre if the query matches a known genre
    genre_filtered = df[df['genre'].str.contains(user_query, case=False, na=False)]

    # If no genre match is found, fallback to the full dataset
    relevant_songs = genre_filtered if not genre_filtered.empty else df

    # Shuffle globally for randomness
    relevant_songs = relevant_songs.sample(frac=1).reset_index(drop=True)

    # Select up to 50 songs as a broad pool
    broad_pool = relevant_songs.head(50)

    # Iterate over the broad pool to collect unique tracks
    for _, row in broad_pool.iterrows():
        if (row['track'], row['artist']) in used_tracks:
            continue  # Skip already used tracks

        # Check valence tag proximity
        if abs(row['valence_tags'] - normalized_polarity) <= 0.2:
            preview_url = get_spotify_preview_url(row['track'], row['artist'])
            if preview_url:  # Only include songs with valid preview URLs
                song_data = {'track': row['track'], 'artist': row['artist'], 'preview_url': preview_url}
                song_list.append(song_data)
                used_tracks.add((row['track'], row['artist']))
                if len(song_list) == 3:
                    break

    # Fallback if less than 3 songs are found
    if len(song_list) < 3:
        remaining_songs = relevant_songs.sample(frac=1).reset_index(drop=True)
        for _, row in remaining_songs.iterrows():
            if (row['track'], row['artist']) in used_tracks:
                continue
            preview_url = get_spotify_preview_url(row['track'], row['artist'])
            if preview_url:  # Ensure only valid preview URLs
                song_data = {'track': row['track'], 'artist': row['artist'], 'preview_url': preview_url}
                song_list.append(song_data)
                used_tracks.add((row['track'], row['artist']))
                if len(song_list) == 3:
                    break

    return song_list

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_playlist", methods=["POST"])
def generate_playlist():
    mood = request.form["mood"]
    try:
        analysis = TextBlob(mood)
        polarity = analysis.sentiment.polarity

        # Select songs based on polarity and user query
        playlist = select_songs_by_query(polarity, mood)

        # Pass the playlist with track, artist, and preview URL to the template
        return render_template("playlist.html", mood=mood, playlist=playlist)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template("playlist.html", mood=mood, playlist=[])

if __name__ == "__main__":
    app.run(debug=True)
