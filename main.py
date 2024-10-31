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
    
    headers = {
        'Authorization': f'Basic {auth_base64}'
    }
    data = {'grant_type': 'client_credentials'}
    
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()
    
    # Debug: Print token response to check if token is retrieved
    print("Spotify Token Response:", response_data)
    
    return response_data.get('access_token', None)


def get_spotify_preview_url(track_name, artist_name):
    """Search for a track on Spotify and return the preview URL."""
    token = get_spotify_token()
    if not token:
        print("Error: No Spotify token retrieved.")
        return None
    
    search_url = 'https://api.spotify.com/v1/search'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'q': f'track:{track_name} artist:{artist_name}',
        'type': 'track',
        'limit': 1
    }
    
    response = requests.get(search_url, headers=headers, params=params)
    response_data = response.json()
    
    # Debugging output
    print(f"\nSearching for Track: {track_name} by Artist: {artist_name}")
    print("Spotify Search Response:", response_data)
    
    # Check if a track is found and if it has a preview URL
    if response_data['tracks']['items']:
        preview_url = response_data['tracks']['items'][0].get('preview_url', None)
        print("Preview URL found:", preview_url)
        return preview_url
    else:
        print("No matching track found on Spotify.")
    return None

def generate_mood_profile(polarity: float, subjectivity: float) -> str:
    """Maps sentiment scores to mood profiles based on polarity and subjectivity."""
    if polarity > 0.5 and subjectivity < 0.5:
        return 'Happy/Energetic'
    elif polarity > 0.5 and subjectivity >= 0.5:
        return 'Calm/Content'
    elif polarity < -0.5:
        return 'Sad/Mellow'
    else:
        return 'Intense/Focused'

def select_songs_by_mood(profile: str) -> list:
    """Filters songs based on the mood profile and adds preview URLs."""
    if profile == 'Happy/Energetic':
        filtered_songs = df[(df['valence_tags'] > 0.7) & (df['arousal_tags'] > 0.7) & (df['dominance_tags'] >= 0.5)]
    elif profile == 'Calm/Content':
        filtered_songs = df[(df['valence_tags'] > 0.7) & (df['arousal_tags'] < 0.5) & (df['dominance_tags'] >= 0.5)]
    elif profile == 'Sad/Mellow':
        filtered_songs = df[(df['valence_tags'] < 0.3) & (df['arousal_tags'] < 0.5) & (df['dominance_tags'] <= 0.5)]
    else:  # Intense/Focused
        filtered_songs = df[(df['valence_tags'] >= 0.5) & (df['arousal_tags'] > 0.7) & (df['dominance_tags'] > 0.7)]

    # Debug: Check the filtered songs
    print(f"Filtered songs for profile '{profile}':", filtered_songs[['track', 'artist']].head())

    song_list = []
    for _, row in filtered_songs.sample(n=3, random_state=random.randint(0, 100)).iterrows():
        print("Processing track:", row['track'], "by artist:", row['artist'])  # Debug track and artist
        preview_url = get_spotify_preview_url(row['track'], row['artist'])
        print("Preview URL:", preview_url)  # Check if preview URL is retrieved
        song_list.append({
            'track': row['track'],
            'artist': row['artist'],
            'preview_url': preview_url
        })
    return song_list

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_playlist", methods=["POST"])
def generate_playlist():
    mood = request.form["mood"]
    
    # Analyze sentiment using TextBlob
    try:
        analysis = TextBlob(mood)
        polarity = analysis.sentiment.polarity
        subjectivity = analysis.sentiment.subjectivity
        
        # Map the sentiment scores to a mood profile
        mood_profile = generate_mood_profile(polarity, subjectivity)
        
        # Select songs based on the mood profile with randomization and preview URLs
        playlist = select_songs_by_mood(mood_profile)
        
        # Pass the playlist with track, artist, and preview URL to the template
        return render_template("playlist.html", mood=mood, playlist=playlist)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template("playlist.html", mood=mood, playlist=["Error generating playlist. Please try again."])

if __name__ == "__main__":
    app.run(debug=True)
