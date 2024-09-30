from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_playlist", methods=["POST"])
def generate_playlist():
    mood = request.form["mood"]  # Get the mood from the form
    
    # For now, we'll use placeholder songs based on mood
    if mood.lower() == "happy":
        playlist = ["Song A", "Song B", "Song C"]
    elif mood.lower() == "sad":
        playlist = ["Song D", "Song E", "Song F"]
    else:
        playlist = ["Song G", "Song H", "Song I"]

    return render_template("playlist.html", mood=mood, playlist=playlist)

if __name__ == "__main__":
    app.run(debug=True)
