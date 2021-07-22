import json
from math import ceil

import argparse
import numpy as np
import pandas as pd
from dotenv import load_dotenv

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
                        help='If declared, it will update the previously created playlists instead of creating new ones')
    parser.add_argument('-l', '--lenght', nargs='?', default=150, type=int,
                        help='Total number of songs per playlist. Default is 150')
    return vars(parser.parse_args())


if __name__ == "__main__":

    # Get all env variables
    load_dotenv()
    spotify_client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    spotify_client_id = os.environ.get("SPOTIFY_CLIENT_ID")

    args = parse_args()

    # Start the spotify user api session and authenticate
    spotify = spotify_user_api(client_id=args['spotify_client_id'],
                               client_secret=args['spotify_client_secret'],
                               redirect_uri='https://www.google.com',
                               scope='playlist-modify-public user-read-private')

    df = load_results(filename='clusterization')
    df = df[['cluster', 'id']]

    clusters = len(df['cluster'].unique())

    if args['replace_playlists'] is True:
        # Recover the file with the created playlists and set a dict with current user's ones
        playlists_df = load_results(filename='playlists')
        playlists_df = playlists_df[playlists_df['user_id'] ==
                                    spotify.user_id]['playlist_id']  # .set_index('user_id')

        # Delete all songs from the existing playlists
        for i in range(len(playlists_df.values)):
            spotify.delete_playlist_songs(playlist=playlists_df.values[i],
                                          songs=True)

        playlists = playlists_df.reset_index()['playlist_id'].to_dict()
        # Create new playlists if needed (more clusters than spotify ids already stored)
        if len(playlists_df.index) < clusters:
            new = clusters - len(playlists_df.index)

            for i in range(new):
                cluster = len(playlists_df.index) + i
                playlist = spotify.create_playlist(
                    name=f'k-means-cluster-{cluster}', description='k-means generated playlist from lastfm data')
                playlists[cluster] = playlist
        else:
            pass
    else:
        # Create new playlists from scratch and save them on the existing created playlists file.
        playlists = {}
        for i in range(clusters):
            cluster = df['cluster'].unique()[i].item()
            playlist = spotify.create_playlist(
                name=f'k-means-cluster-{cluster}', description='k-means generated playlist from lastfm data')

            # Generate a dict with the clusters and the playlist id - this will be used to add the songs later
            playlists[cluster] = playlist

    # Overwrite previously saved playlist ids from this user
    #   It is not possible to choose which playlists to user or store: all is lost
    playlists_df = load_results(filename='playlists')
    playlists_df = playlists_df[playlists_df['user_id'] != spotify.user_id]

    tempdf = pd.DataFrame(data=playlists.values(),
                          columns=['playlist_id'])
    tempdf['user_id'] = spotify.user_id

    playlists_df = playlists_df.append(other=tempdf,
                                       ignore_index=True)

    save_results(filename='playlists', df=playlists_df)

    # ### Adding songs to the playlists

    for key in playlists:
        tempdf = df[df['cluster'] == key].sample(args['lenght'])
        # Break the ids in chunks respecting the api limitation of batches of 100s
        splits = ceil(len(tempdf)/100)
        chunks = np.array_split(tempdf, splits)
        for i in range(len(chunks)):
            spotify.add_song_to_playlist(songs=chunks[i]['id'].tolist(),
                                         playlist=playlists[key])

    print("Playlists created on Spotify!")
