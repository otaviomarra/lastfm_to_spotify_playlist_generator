import os
import sys
import warnings

# import argparse
import pandas as pd
from dotenv import load_dotenv

from utils.utils import *
from utils.spotify_api import spotify_requests


if __name__ == "__main__":

    # Get all env variables
    load_dotenv()
    spotify_client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    spotify_client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    user = os.environ.get("LASTFM_USER")

    tracks = load_user_results(filename='lastfm_played_tracks', user=user)
    tracks.drop(tracks.columns[2], axis=1, inplace=True)
    tracks = tracks.drop_duplicates()

    stored_tracks_ids = load_results(filename='spotify_tracks_ids')
    if stored_tracks_ids is not None:
        # To ensure we are only making api calls for non-stored data
        tracks = pd.merge(left=tracks,
                          right=stored_tracks_ids,
                          how='outer',
                          left_on=['song', 'artist'],
                          right_on=['song', 'artist'],
                          indicator=True)
        tracks = tracks[tracks['_merge'] == 'left_only']
        tracks = tracks.drop(columns='_merge', axis=1)

    else:
        pass

    # Spotify API  - Get Song IDs
    spotify = spotify_requests(client_id=spotify_client_id,
                               client_secret=spotify_client_secret)

    # Start the api calls and save the spotify song id on a new columns of the dataframe
    print("Retrieving spotify ids for a few songs")
    tracks['sp_id'] = tracks.apply(lambda x: spotify.find_song_id(
        song_name=x['song'], band_name=x['artist']), axis=1)

    # Creating a boolean column for not found song ids
    tracks['no_id'] = tracks['sp_id'].apply(lambda x: x == 'not_found')

    if stored_tracks_ids is not None:
        tracks = tracks.append(stored_tracks_ids)

    save_results(filename='spotify_tracks_ids', df=tracks)

    os.system('clear')
    found_ratio = round(
        (len(tracks[tracks['sp_id'] != 'not_found'])/len(tracks)*100))

    print('\n Getting the song features...')

    tracks = tracks[tracks['no_id'] == False]

    # Create and empty DF to store the results
    song_features = spotify.get_songs_features(ids=tracks['sp_id'])

    # song_features.set_index('id', inplace=True)
    stored_song_features = load_results(filename='spotify_songs_features')

    if stored_song_features is not None:
        song_features = song_features.append(stored_song_features)

    save_results(filename='spotify_songs_features', df=song_features)

    print('Done! Spotify songs features and ids retrieved')
