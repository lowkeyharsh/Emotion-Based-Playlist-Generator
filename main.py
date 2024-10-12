import pandas as pd
from flask import Flask, render_template, request
from textblob import TextBlob

app = Flask(__name__)

# Load the Musical Sentiment Dataset from the Data folder
df = pd.read_csv('Data/musical_sentiment.csv')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_playlist", methods=["POST"])
def generate_playlist():
    mood = request.form["mood"]  # Get the mood from the form
    
    # Analyze sentiment using TextBlob
    analysis = TextBlob(mood)
    polarity = analysis.sentiment.polarity  # Polarity: -1 to 1 (negative to positive)
    subjectivity = analysis.sentiment.subjectivity  # Subjectivity: 0 to 1 (objective to subjective)
    
    # Basic mapping logic using valence_tags from dataset
    # If polarity is positive, select songs with higher valence_tags (>0.5)
    if polarity > 0:
        playlist = df[df['valence_tags'] > 0.5][['track', 'artist']].head(3)
    # If polarity is negative, select songs with lower valence_tags (<0.5)
    elif polarity < 0:
        playlist = df[df['valence_tags'] < 0.5][['track', 'artist']].head(3)
    # If neutral, select random songs
    else:
        playlist = df[['track', 'artist']].sample(3)

    # Create a list of strings like "song_name by artist_name"
    formatted_playlist = [f"{row['track']} by {row['artist']}" for index, row in playlist.iterrows()]

    return render_template("playlist.html", mood=mood, playlist=formatted_playlist)

if __name__ == "__main__":
    app.run(debug=True)
