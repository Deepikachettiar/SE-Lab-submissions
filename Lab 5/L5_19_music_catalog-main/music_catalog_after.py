"""A small music catalog demo with playlist storage and popularity checks."""

import json
import secrets
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE songs (id INTEGER PRIMARY KEY, "
    "title TEXT, artist TEXT, plays INTEGER)"
)


def add_song(title, artist, plays=0, playlist=None):
    """Add a song to the in-memory database and return the playlist."""
    if playlist is None:
        playlist = []

    conn.execute(
        "INSERT INTO songs (title, artist, plays) VALUES (?, ?, ?)",
        (title, artist, plays),
    )
    playlist.append(title)
    return playlist


def shuffle_pick():
    """Return a random song ID from the database."""
    ids = [row[0] for row in conn.execute("SELECT id FROM songs")]
    if not ids:
        return None
    return secrets.choice(ids)


def popularity(title):
    """Return popularity category for a song title."""
    row = conn.execute(
        "SELECT plays FROM songs WHERE title = ?",
        (title,),
    ).fetchone()
    if row is None:
        return "unknown"
    return "popular" if row[0] > 100 else "niche"


def save_playlist(playlist):
    """Serialize a playlist to a JSON-safe byte string."""
    return json.dumps(playlist).encode("utf-8")


def load_playlist(blob):
    """Deserialize a playlist from JSON bytes."""
    return json.loads(blob.decode("utf-8"))


def total_plays():
    """Return the total number of plays across all songs."""
    result = conn.execute(
        "SELECT COALESCE(SUM(plays), 0) FROM songs"
    ).fetchone()[0]
    return result if result is not None else 0


def main():
    """Run the sample playlist demo."""
    playlist = add_song("Aurora", "Nila", 250)
    add_song("Monsoon", "Kavya", 40, playlist)
    blob = save_playlist(playlist)
    loaded_playlist = load_playlist(blob)
    if len(loaded_playlist) > 1:
        print("multi-song playlist")
    print(
        popularity("Aurora"),
        popularity("Monsoon"),
        shuffle_pick(),
        total_plays(),
    )


if __name__ == "__main__":
    main()
