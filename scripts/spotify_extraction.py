import os
import argparse
import pandas as pd

from utils.utils import *
from utils.spotify_api import spotify_requests


def parse_args():
    """
    Parse arguments passed when calling the scripts

    Returns a dict with all the arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('spotify_client_id', type=str,
                        help='The spotify app client id')
    parser.add_argument('spotify_client_secret', type=str,
                        help='The spotify app client secret')
    parser.add_argument('-d', '--delete_cache', action='store_true',
                        help='Delete the cached requests at the end of execution (will make further executions slower)')
    return vars(parser.parse_args())


if __name__ == "__main__":

    args = parse_args()

    initiate_cache(filename='spotify_song_ids_cache')

    tracks = load_results(filename='lastfm_played_tracks')
    tracks.drop(tracks.columns[2], axis=1, inplace=True)
    tracks = tracks.drop_duplicates()

    # Spotify API  - Get Song IDs

    # Authenticate on Spotify
    spotify = spotify_requests(client_id=args['spotify_client_id'],
                               client_secret=args['spotify_client_secret'])

    # Start the api calls and save the spotify song id on a new columns of the dataframe
    print("Retrieving spotify ids for all songs")
    tracks['sp_id'] = tracks.apply(lambda x: spotify.find_song_id(
        song_name=x['song'], band_name=x['artist']), axis=1)

    tracks['no_id'] = tracks['sp_id'].apply(lambda x: x == 'not_found')

    save_results(filename='spotify_tracks_ids', df=tracks)

    os.system('clear')
    found_ratio = round(
        (len(tracks[tracks['sp_id'] != 'not_found'])/len(tracks)*100))

    print(f'Spotify id found for {found_ratio}% of the Lastfm tracks')
    print('\n Getting the song features...')

    initiate_cache(filename='spotify_song_features_cache')

    tracks = tracks[tracks['no_id'] == False]

    # Create and empty DF to store the results
    song_features = spotify.get_songs_features(ids=tracks['sp_id'])

    #song_features.set_index('id', inplace=True)
    save_results(filename='spotify_songs_features', df=song_features)
    if args['delete_cache'] is True:
        remove_cache(filename='spotify_song_features_cache')
        remove_cache(filename='spotify_song_ids_cache')

    print('Done! Spotify songs features and ids retrieved')
