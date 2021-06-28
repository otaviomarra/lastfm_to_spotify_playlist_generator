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
                        help='If declared, it will try to use the same playlists previously created for this user, with this script or create new ones')
    parser.add_argument('-l', '--lenght', nargs='?', const=150, type=int,
                        help='Total number of songs per playlist. Default is 150')
    return vars(parser.parse_args())


if __name__ == "__main__":

    args = parse_args()

    spotify = spotify_user_api(client_id=args['spotify_client_id'],
                               client_secret=args['spotify_client_secret'],
                               scope='playlist-modify-public user-read-private')

    df = load_results(filename='clusterization')
    df = df[['label', 'id']]

    clusters = len(df['label'].unique())

    # **IMPORTANT:** the playlists should either be created at the same time or we'd need to manually create the playlists array with their ids
    # If needed, you can manually delete the playlists on Spotify and then re-create them

    if args['replace_playlists'] == True:
        # Recover the file with the created playlists and set a dict with current user's ones
        playlists_df = load_results(filename='playlists')
        playlists_df = playlists_df[playlists_df['user_id'] ==
                                    spotify.user_id]['playlist_id'].set_index('user_id')

        playlists = playlists_df.to_dict()

        # Create new playlists if needed (more clusters than already stored)
        if len(playlists_df.index) < clusters:
            new = clusters - len(playlists_df.index)
            for i in range(new):
                label = clusters + i + 1
                playlist = spotify.create_playlist(
                    name=f'k-means-cluster-0 {label}', description='k-means generated playlist. have fun')
                playlists[label] = playlist
    else:
        # Create new playlists from scratch and save them on the existing created playlists file.
        playlists = {}
        for i in range(clusters):
            label = df['label'].unique()[i].item()
            playlist = spotify.create_playlist(
                name=f'k-means-cluster-0 {label}', description='k-means generated playlist. have fun')

            # Generate a dict with the labels and the playlist id - this will be used to add the songs later
            playlists[label] = playlist

    # Overwrite previously saved playlist ids from this user - It is not possible to choose which playlists to overwrite
    playlists_df = load_results(filename='playlists')
    playlists_df = playlists_df[playlists_df['user_id'] != spotify.user_id]
    playlists_df = playlists_df.append(
        pd.DataFrame.from_dict(playlists, orient='index'), ignore_index=True)
    save_results(filename='playlists', df=playlists_df)

    # ### Adding songs to the playlists

    for key in playlists:
        tempdf = df[df['label'] == key].sample(args['lenght'])
        # Break the ids in chunks (respecting the api limitation of batches of 100s)
        splits = ceil(len(tempdf)/100)
        chunks = np.array_split(tempdf, splits)
        # format and call the function to every chunk
        for i in range(len(chunks)):
            spotify.add_song_to_playlist(songs=chunks[i],
                                         playlist=playlist[key])
