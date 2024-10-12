from flask import Flask, render_template, request
from textblob import TextBlob

app = Flask(__name__)

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

    # For now, we'll print out polarity and subjectivity just for testing
    print(f"Polarity: {polarity}, Subjectivity: {subjectivity}")

    # Placeholder: Use these values to select a playlist (will integrate dataset later)
    if polarity > 0:
        playlist = ["Happy Song 1", "Happy Song 2", "Happy Song 3"]
    elif polarity < 0:
        playlist = ["Sad Song 1", "Sad Song 2", "Sad Song 3"]
    else:
        playlist = ["Neutral Song 1", "Neutral Song 2", "Neutral Song 3"]

    return render_template("playlist.html", mood=mood, playlist=playlist)

if __name__ == "__main__":
    app.run(debug=True)
