import json
from math import ceil

import argparse
import numpy as np
import pandas as pd
import requests as re

from utils.utils import save_results, load_results
from utils.spotify_api import spotify_user_api


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
    parser.add_argument('-r', '--replace_playlists', action='store_true',
                        help='If declared, it will delete the previous playlists created for this user with this script')
    return vars(parser.parse_args())


def add_songs_to_playlist(songs, playlist):
    """
    Makes the API request to add songs on an existing Spotify playlist
    Receives a string with all the songs uris on a csv format (up to 100 at a time) and the playlist id
    It works on batches of up to 100 songs at a single time

    Returns None
    """
    url = f'https://api.spotify.com/v1/playlists/{playlist}/tracks'
    data = json.dumps({'uris': songs})
    response = re.post(url=url, data=data, headers=headers)
    print(response.json())


if __name__ == "__main__":

    args = parse_args()

    spotify = spotify_user_api(client_id=args['spotify_client_id'],
                               client_secret=args['spotify_client_secret'],
                               scope='playlist-modify-public user-read-private')

    df = load_results(filename='clusterization')
    df = df[['label', 'id']]
    # Generate the spotify uris following their standardized pattern
    df['uris'] = 'spotify:track:' + df['id']

    # authentication. for now it is a manyally requst token but I'll come back to that later

    headers = {
        f'Content-Type":"application/json", "Authorization":"Bearer {access_token}'}
    user_id = 'ommarra'

    # **IMPORTANT:** the playlists should either be created at the same time or we'd need to manually create the playlists array with their ids
    # If needed, you can manually delete the playlists on Spotify and then re-create them

    endpoint_url = f'https://api.spotify.com/v1/users/{user_id}/playlists'

    playlists = {}
    for i in range(len(df['label'].unique())):
        label = df['label'].unique()[i].item()
        playlist_name = f'k-means-cluster-0 {label}'
        request_body = json.dumps({
            "name": playlist_name,
            "description": "k means generated. probably shitty",
            "public": True
        })
        r = re.post(url=endpoint_url, data=request_body, headers=headers)
        # generate a dict with the labels and the playlist id - this will be used to add the songs later
        playlists[label] = r.json()['id']

    # ### Adding songs to the playlists

    for key in playlists:
        playlist = playlists[key]
        # 150 songs per playlist is a good starter. Later on I'd like to also limit the number of songs from the same artist
        tempdf = df[df['label'] == key].sample(150)
        # break it even to post the ids in chunks (respecting the api limitation off batches of 100s)
        splits = ceil(len(tempdf)/100)
        chunks = np.array_split(tempdf, splits)
        # format and call the function to every chunk
        for i in range(len(chunks)):
            songs = chunks[i]['uris'].to_json(orient='records')
            add_songs_to_playlist(songs=json.loads(songs), playlist=playlist)
