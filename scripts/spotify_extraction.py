import time
import json
from math import ceil
from datetime import date, timedelta, datetime

import numpy as np
import pandas as pd
import requests_cache
import requests as re

from utils.utils import *


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


def spotify_app_authenticate(client_id, client_secret):
    """
    Authenticate the spotify app to retrieve a client_secret

    Arguments:
        client_id (string): the spotify app client id

        client_secret (string): the spotify app client secret

    Returns a string with the client_secret 
    """
    # Authentication - getting an access token
    auth_response = re.post('https://accounts.spotify.com/api/token', {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })

    # save the access token
    return auth_response.json()['access_token']


def search_song_request(song_name, band_name, headers):
    """
    Makes the search song api request that returns the json response

    Arguments:
        song_name (string): name of the song

        band_name (string): name of the band

        headers (string): headers with the access token to make the api request

    Returns  a json with the 50 first results for the band + song name search on spotify
    """
    r = re.get('https://api.spotify.com/v1/search?' + 'q=artist:' + band_name + '%20track:' +
               song_name + '&market:from_token' + '&type=track&limit=50&include_external=audio', headers=headers)
    try:
        return r.json()['tracks']['items']
    except:
        return None


def get_spotify_song_id(song_name, band_name, headers):
    """
    Makes the search song api request and iterate on the responde to get the spotify song id

    Arguments:
        song_name (string): name of the song

        band_name (string): name of the band

        headers (string): headers with the access token to make the api request

    Returns the spotify song id for the song (or 'not_found' if we couldn't find it)
    """
    response = search_song_request(song_name, band_name)
    if response is not None:
        for i in range(len(response)):
            # there must be a better way of doing this but it'll work for now:
            # we iterate through the entire artist list - there is a lot of useless data in the response
            if response[i]['album']['artists'][0]['name'] == band_name:
                return response[i]['id']
            else:
                continue
    # if no returns, we could not find id, so it returns not_found
    return 'not_found'


def get_song_features(ids, headers):
    """
    API request to get Spotify's song features from the Spotify track id
    Receives a string containing a list of spotify_ids on csv format (the api request works with up to 100 ids at a time)
    Returns a json file with all the song features for the ids
    """
    r = re.get('https://api.spotify.com/v1/audio-features?ids=' +
               ids, headers=headers)
    return r.json()


if __name__ == "__main__":

    args = parse_args()

    initiate_cache(filename='spotify_song_ids_cache')

    tracks = load_results(filename='lastfm_played_tracks')
    tracks.drop(tracks.columns[2], axis=1, inplace=True)
    tracks = tracks.drop_duplicates()

    # Spotify API  - Get Song IDs

    # Authenticate on Spotify
    access_token = spotify_app_authenticate(
        client_id=args['spotify_client_id'],
        client_secret=args['spotify_client_secret'])

    headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}

    # Start the api calls and save the spotify song id on a new columns of the dataframe
    print("Retrieving spotify ids for all songs")
    tracks['sp_id'] = tracks.apply(lambda x: get_spotify_song_id(
        song_name=x['song_name'], band_name=x['band_name'], headers=headers), axis=1)

    tracks['no_id'] = tracks['sp_id'].apply(lambda x: x == 'not_found')

    save_results(filename='spotify_tracks_ids', df=tracks)

    # Get Song Features from Spotify

    initiate_cache(filename='spotify_song_features_cache')

    tracks = tracks[tracks['no_id'] == False]

    # Create and empty DF to store the results
    cols = ['danceability',
            'energy',
            'key',
            'loudness',
            'mode',
            'speechiness',
            'acousticness',
            'instrumentalness',
            'liveness',
            'valence',
            'tempo',
            'type',
            'id',
            'uri',
            'track_href',
            'analysis_url',
            'duration_ms',
            'time_signature', ]

    song_features = pd.DataFrame(columns=cols)

    # we can make a single request with a csv of up to 100 song ids at once. So we break the dataframe into smaller lists to make multiple requests
    splits = ceil(len(tracks)/100)
    chunks = np.array_split(tracks, splits)

    for i in range(len(chunks)):
        # transform the IDs from each chunk into a csv list (string format) to be used at the api request
        song_ids = chunks[i]['sp_id'].to_string(
            header=False, index=False).replace('\n ', ',').lstrip()
        # make the api request
        r = get_song_features(song_ids, headers)
        # normalize and append the reults to a final dataframe
        temp = pd.json_normalize(r['audio_features'])
        song_features = song_features.append(temp)

    #song_features.set_index('id', inplace=True)
    save_results(filename='spotify_songs_features', df=song_features)
    if args['delete_cache'] is True:
        remove_cache(filename='spotify_song_features_cache')
        remove_cache(filename='spotify_song_ids_cache')

    print('Done! Spotify songs features and ids retrieved')
