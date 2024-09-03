import time, random, re
from collections import OrderedDict

# Function to get metadata and audio features for a list of searched (song, artist)
def get_song_info(spotify, playlist, batch, mode='default'):
    start = time.time()
    songs_metadata = OrderedDict()
    track_info = []  # song name, artists, popularity
    batch_ids = []
    song_ids = []
    batches_processed = 0
    songs_processed = 0

    for song in playlist:
        result = []
        track = None

        if mode == 'search':
            search_query = f"track:{song[0]} artist:{song[1]}"
            result = spotify.search(q=search_query, type="track", limit=1)
            if result['tracks']['items']:
                track = result['tracks']['items'][0]

        elif mode == 'playlist':
            track = song

        if track:
            # Extract song label
            track_name = track['name']
            artist_names = [artist['name'] for artist in track['artists']]
            artists = ', '.join(artist_names)
            track_labels = (track_name, artists, track['popularity'])
            track_info.append(track_labels)

            # Extract id to batch
            tokens = re.split(r"[\/]", track['href'])
            track_id = tokens[5]
            batch_ids.append(track_id)
            songs_processed += 1

            if songs_processed % batch == 0 or songs_processed == len(playlist):
                # Get audio features for the track batch
                audio_features = get_audio_features(spotify, batch_ids)

                for idx, audio_feature in enumerate(audio_features):
                    idx += batches_processed * batch
                    current_song = f"{track_info[idx][0]} - {track_info[idx][1]}"

                    song_ids.append(audio_feature['id'])

                    # Process audio features for each track in the batch
                    feature_data = [
                        track_info[idx][2],  # popularity #0
                        audio_feature['danceability'], #1
                        audio_feature['energy'], #2
                        audio_feature['key'], #3
                        audio_feature['loudness'], #4
                        audio_feature['speechiness'], #5
                        audio_feature['acousticness'], #6
                        audio_feature['instrumentalness'], #7
                        audio_feature['liveness'], #8
                        audio_feature['valence'], #9
                        audio_feature['tempo'], #10
                        audio_feature['time_signature'] #11
                    ]
                    songs_metadata[current_song] = feature_data

                batch_ids = []  # Clear batch IDs for next batch
                batches_processed += 1

        else:
            print(f"    {song} - {artist} not found!")

    return songs_metadata, song_ids

def get_playlist_tracks(spotify, playlist_id):
    tracks = []
    results = spotify.playlist_tracks(playlist_id)
    playlist_info = spotify.playlist(playlist_id)  # Retrieve playlist information
    playlist_title = playlist_info['name']  # Extract the title of the playlist

    for item in results['items']:
        track = item['track']
        tracks.append(track)
    
    return tracks, playlist_title

# Function to get recommendations for a playlist
def get_track_recommendations(spotify, playlist, mean):

    results = []

    for track in playlist:
        # returns 20 recommendations [result] for each track, keeps within the confines of the playlist traits
        result = spotify.recommendations(seed_tracks=[track], limit=12)
        for track in result['tracks']:
            results.append(track)

    songs_metadata, song_ids = get_song_info(spotify, results, 100, 'playlist')
    return songs_metadata, song_ids

def get_audio_features(spotify, track_ids):
    return spotify.audio_features(track_ids)