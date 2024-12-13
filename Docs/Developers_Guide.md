
---

## Installation & Setup

Ensure you’ve followed the installation and setup instructions from the [User’s Guide](../README.md).

**Additional Setup for Developers:**
1. **Logging**: All application events and errors are logged in `app.log`. Use this file for debugging during development.
2. **API Credentials**: Replace `CLIENT_ID` and `CLIENT_SECRET` in `config.py` with your Spotify Developer credentials.
3. **Testing**: Run the app locally to test new features or debug issues before deployment.

---

## Code Walkthrough

### 1. User Authentication
- **Files Involved**: `main.py`, `signup.html`, `login.html`
- **Flow**:
    - Users can sign up and log in.
    - Credentials are stored in a dictionary (can be extended to use a database in `app.db`).
    - Sessions are managed using Flask’s session management.
- **Key Functions**:
    - `signup`: Handles user registration.
    - `login`: Validates user credentials and starts a session.
    - `logout`: Ends the session for the logged-in user.

---

### 2. Mood Input & Sentiment Analysis
- **Files Involved**: `index.html`, `main.py`
- **Flow**:
    - Users input a mood (e.g., "happy", "sad") on the home page.
    - The `TextBlob` library analyzes the sentiment of the mood.
    - Sentiment polarity is normalized and passed to the playlist generator.
- **Key Functions**:
    - `generate_playlist`: Handles the mood input, analyzes the sentiment, and generates a playlist.

---

### 3. Playlist Generation
- **Files Involved**: `main.py`, `playlist.html`
- **Flow**:
    - The `select_songs_by_query` function filters songs from the dataset based on:
        - Genre match.
        - Proximity of `valence_tags` to the normalized polarity.
    - A maximum of 5 songs are selected, and their Spotify links are displayed.
- **Key Functions**:
    - `select_songs_by_query`: Implements the filtering logic for song recommendations.
    - **Spotify Link Construction**:
        - If a `spotify_id` exists for a song, a link is generated:  
          `https://open.spotify.com/track/<spotify_id>`.

---

## Known Issues

### Minor Issues
1. **Dataset Limitations**: 
   - The `musical_sentiment.csv` dataset may not contain sufficient variety for all moods.
2. **UI Enhancements**:
   - While functional, the UI could benefit from further visual improvements.

### Major Issues
1. **API Dependency**:
   - Missing or invalid Spotify API credentials will prevent the app from generating valid Spotify links.
2. **Scalability**:
   - Filtering large datasets could lead to performance bottlenecks.

---

## Future Work

1. **Dataset Expansion**:
    - Integrate APIs to fetch real-time data and dynamically update the dataset.

2. **Enhanced Recommendation Logic**:
    - Use machine learning models to improve mood-to-song mapping beyond sentiment analysis.

3. **Advanced Authentication**:
    - Store user credentials securely using hashing algorithms.
    - Implement OAuth for third-party authentication.

4. **Error Handling**:
    - Improve error messages for users.
    - Add automated testing to ensure robustness.

5. **Track Previews**:
    - Give the ability to preview a 30 second clip from the song using Spotify's API in the app itself.

---

## Screenshots

**Signup Page:**
<img width="1302" alt="Screenshot 2024-12-13 at 11 25 13 PM" src="https://github.com/user-attachments/assets/6ca5bec0-b0b9-4772-9f95-074adcbc7bc3" />

**Login Page:**
<img width="1302" alt="Screenshot 2024-12-13 at 11 25 28 PM" src="https://github.com/user-attachments/assets/31ac15ab-0ca4-425c-b985-c975262c1222" />

**Mood Input Page:**
<img width="1300" alt="Screenshot 2024-12-13 at 11 28 10 PM" src="https://github.com/user-attachments/assets/ebed9950-aea4-4c02-b1c1-a2aa4cce6812" />

**Generated Playlist:**
<img width="1311" alt="Screenshot 2024-12-13 at 11 28 22 PM" src="https://github.com/user-attachments/assets/73cf98ab-328e-4742-b65f-011cefbd040e" />

---

**For Developers**:  
If you have any questions, feel free to open an issue in the repository or contact the project maintainers.
