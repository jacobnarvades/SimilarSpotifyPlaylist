import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def auth_credentials():
    # Set up a session
    client_id = "f09683829a904df38515406f320e0fc1"
    client_secret = "e808ee01467440f6ad0b4ef4ade9c7bf"
    
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify