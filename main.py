import pandas as pd
import random
from flask import Flask, render_template, request
from textblob import TextBlob

app = Flask(__name__)

# Load the Musical Sentiment Dataset from the Data folder
df = pd.read_csv('Data/musical_sentiment.csv')

def generate_mood_profile(polarity: float, subjectivity: float) -> str:
    """
    Maps sentiment scores to mood profiles based on polarity and subjectivity.
    
    Args:
        polarity (float): Sentiment polarity, ranges from -1 (negative) to 1 (positive).
        subjectivity (float): Sentiment subjectivity, ranges from 0 (objective) to 1 (subjective).
    
    Returns:
        str: The identified mood profile, such as 'Happy/Energetic' or 'Sad/Mellow'.
    """
    if polarity > 0.5 and subjectivity < 0.5:
        return 'Happy/Energetic'
    elif polarity > 0.5 and subjectivity >= 0.5:
        return 'Calm/Content'
    elif polarity < -0.5:
        return 'Sad/Mellow'
    else:
        return 'Intense/Focused'

def select_songs_by_mood(profile: str) -> list:
    """
    Filters songs based on the mood profile using valence, arousal, and dominance tags.
    
    Args:
        profile (str): The mood profile used to filter songs.
    
    Returns:
        list: A randomized list of dictionaries containing song and artist names.
    """
    try:
        if profile == 'Happy/Energetic':
            filtered_songs = df[(df['valence_tags'] > 0.7) & (df['arousal_tags'] > 0.7) & (df['dominance_tags'] >= 0.5)]
        elif profile == 'Calm/Content':
            filtered_songs = df[(df['valence_tags'] > 0.7) & (df['arousal_tags'] < 0.5) & (df['dominance_tags'] >= 0.5)]
        elif profile == 'Sad/Mellow':
            filtered_songs = df[(df['valence_tags'] < 0.3) & (df['arousal_tags'] < 0.5) & (df['dominance_tags'] <= 0.5)]
        else:  # Intense/Focused
            filtered_songs = df[(df['valence_tags'] >= 0.5) & (df['arousal_tags'] > 0.7) & (df['dominance_tags'] > 0.7)]
        
        # Ensure there are enough songs in the filtered list
        assert len(filtered_songs) >= 3, "Not enough songs match the criteria for this profile."
        
        # Randomize selection
        song_list = filtered_songs[['track', 'artist']].sample(n=3, random_state=random.randint(0, 100)).to_dict(orient='records')
        return song_list
    
    except AssertionError as e:
        print(f"Error: {e}")
        return [{"track": "Fallback Song", "artist": "Various Artists"}]  # Fallback option

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
        
        # Select songs based on the mood profile with randomization
        playlist = select_songs_by_mood(mood_profile)
        
        # Format playlist for display
        formatted_playlist = [f"{song['track']} by {song['artist']}" for song in playlist]
        return render_template("playlist.html", mood=mood, playlist=formatted_playlist)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template("playlist.html", mood=mood, playlist=["Error generating playlist. Please try again."])

if __name__ == "__main__":
    app.run(debug=True)
