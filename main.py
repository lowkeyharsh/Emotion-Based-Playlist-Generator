import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session
from textblob import TextBlob
from config import CLIENT_ID, CLIENT_SECRET  # Import credentials from config.py

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Replace with an actual secret key for production

# Placeholder for user data (in-memory for now)
users = {}

# Load the musical sentiment dataset
df = pd.read_csv('Data/musical_sentiment.csv')

def normalize(value: float) -> float:
    """Normalize a value between -1 and 1 to 0 and 1."""
    return (value + 1) / 2

def select_songs_by_query(polarity: float, user_query: str) -> list:
    """
    Filters songs based on normalized polarity, genre, and emotional tags,
    and returns song metadata (track name, artist, Spotify link).
    """
    normalized_polarity = normalize(polarity)  # Normalize polarity to 0-1
    song_list = []

    # Filter by genre if the query matches a known genre
    genre_filtered = df[df['genre'].str.contains(user_query, case=False, na=False)]

    # Use the filtered dataset or fallback to the full dataset
    relevant_songs = genre_filtered if not genre_filtered.empty else df

    # Shuffle the dataset for randomness
    relevant_songs = relevant_songs.sample(frac=1).reset_index(drop=True)

    # Adjust proximity threshold for valence
    for _, row in relevant_songs.iterrows():
        if abs(row['valence_tags'] - normalized_polarity) <= 0.3:
            song_data = {
                'track': row['track'],
                'artist': row['artist'],
                'spotify_link': f"https://open.spotify.com/track/{row['spotify_id']}" if pd.notnull(row['spotify_id']) else "#"
            }
            song_list.append(song_data)
            if len(song_list) >= 5:  # Stop after collecting 5 songs
                break

    # Fallback if less than 5 songs are found
    if len(song_list) < 5:
        remaining_songs = relevant_songs.sample(frac=1).reset_index(drop=True)
        for _, row in remaining_songs.iterrows():
            song_data = {
                'track': row['track'],
                'artist': row['artist'],
                'spotify_link': f"https://open.spotify.com/track/{row['spotify_id']}" if pd.notnull(row['spotify_id']) else "#"
            }
            song_list.append(song_data)
            if len(song_list) >= 5:
                break

    return song_list

@app.route("/")
def home():
    if "username" in session:
        return render_template("index.html", username=session["username"])
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            flash("Username already exists. Please choose another.", "error")
            return redirect(url_for("signup"))

        users[username] = password
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Debugging print to ensure username and password are captured
        print(f"Username: {username}, Password: {password}")

        if username in users:
            if users[username] == password:  # Check if password matches
                session["username"] = username
                flash("Login successful!", "success")
                return redirect(url_for("home"))
            else:
                flash("Incorrect password. Please try again.", "error")
        else:
            flash("Username not found. Please sign up first.", "error")
        
        # Redirect back to the login page if there's an error
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route("/generate_playlist", methods=["POST"])
def generate_playlist():
    if "username" not in session:
        return redirect(url_for("login"))

    mood = request.form["mood"]
    try:
        analysis = TextBlob(mood)
        polarity = analysis.sentiment.polarity

        # Select songs based on polarity and user query
        playlist = select_songs_by_query(polarity, mood)

        # Pass the playlist with track and artist names to the template
        return render_template("playlist.html", mood=mood, playlist=playlist)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template("playlist.html", mood=mood, playlist=[])


if __name__ == "__main__":
    app.run(debug=True)

