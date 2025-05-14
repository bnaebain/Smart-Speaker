import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=scope
))
def get_active_device_id():
    devices = sp.devices()["devices"]
    if not devices:
        return None
    return devices[0]["id"]  # You could also prefer specific device names

def play(query=""):
    device_id = get_active_device_id()
    if not device_id:
        raise Exception("No active Spotify device found. Please open Spotify on a device.")

    if not query:
        sp.start_playback(device_id=device_id)
        return "🎵 Resuming playback."

    # 1. Try playlist first
    try:
        playlist_results = sp.search(q=query, type="playlist", limit=5)
        playlists_data = playlist_results.get("playlists")
        playlists = playlists_data.get("items", []) if playlists_data else []

        print("DEBUG: Playlist search results:", [pl["name"] for pl in playlists])  # optional logging

        # Try exact or partial match
        for pl in playlists:
            if query.lower() in pl["name"].lower():
                uri = pl["uri"]
                sp.start_playback(device_id=device_id, context_uri=uri)
                return f"🎵 Now playing playlist: {pl['name']}."

        # Fall back to first playlist if available
        if playlists:
            uri = playlists[0]["uri"]
            sp.start_playback(device_id=device_id, context_uri=uri)
            return f"🎵 Now playing playlist: {playlists[0]['name']}."
    except Exception as e:
        print(f"DEBUG: Playlist search failed with error: {e}")

    # 2. Try artist
    artist_results = sp.search(q=query, type="artist", limit=1)
    artists = artist_results.get("artists", {}).get("items", [])
    if artists:
        artist_id = artists[0]["id"]
        top_tracks = sp.artist_top_tracks(artist_id)["tracks"]
        if top_tracks:
            uris = [track["uri"] for track in top_tracks[:5]]
            sp.start_playback(device_id=device_id, uris=uris)
            return f"🎵 Now playing top tracks by {artists[0]['name']}."

    # 3. Try track
    track_results = sp.search(q=query, type="track", limit=1)
    tracks = track_results.get("tracks", {}).get("items", [])
    if tracks:
        uri = tracks[0]["uri"]
        sp.start_playback(device_id=device_id, uris=[uri])
        return f"🎵 Now playing {tracks[0]['name']} by {tracks[0]['artists'][0]['name']}."

    raise Exception(f"No music found for: {query}")
    
def pause():
    sp.pause_playback()

def skip():
    sp.next_track()

def current_track():
    current = sp.current_playback()
    if current and current["is_playing"]:
        track = current["item"]
        name = track["name"]
        artist = ", ".join([a["name"] for a in track["artists"]])
        return f"Currently playing: {name} by {artist}"
    return "No music is currently playing."