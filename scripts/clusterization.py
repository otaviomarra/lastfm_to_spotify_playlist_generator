import os
import warnings

import argparse
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from utils.utils import *


def parse_args():
    """
    Parse arguments passed when calling the scripts

    Returns a dict with all the arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('clusters', type=int,
                        help='Number of clusters to be generated')
    parser.add_argument('-r', '--random_state', default=1, type=int,
                        help='Your lucky number (random state for the Kmeans model). Default is 1')
    parser.add_argument('-a', '--algorithm', default='auto', type=str,
                        help="Algorithm for the KMeans clusterization. Check the documentation for more info: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html")
    return vars(parser.parse_args())


if __name__ == "__main__":

    load_dotenv()
    user = os.environ.get("LASTFM_USER")

    warnings.filterwarnings("ignore")
    args = parse_args()

    features = load_results(filename='spotify_songs_features')
    played = load_user_results(filename='lastfm_played_tracks', user=user)
    ids = load_results(filename='spotify_tracks_ids')

    # Dataprep - join the data from multiple sources on a single DF
    df = played.join(features.join(ids.set_index('sp_id'), on='id').set_index(
        ['artist', 'song']), on=['artist', 'song'], how='inner')
    df.drop(columns=['unix_timestamp', 'key', 'mode', 'type',
                     'uri', 'track_href', 'analysis_url'],
            axis=1,
            inplace=True)
    df.drop_duplicates(inplace=True)

    # Remove features not bo be used -it can be adjusted by the user
    df.drop(columns=['speechiness', 'liveness', 'danceability'],
            axis=1,
            inplace=True)

    # Removing the columns not to be used on the clusterization
    X = df.drop(columns=['artist', 'song', 'id', 'duration_ms',
                'time_signature', 'no_id', 'tempo'], axis=1)

    # Normalize all features to values between 0 and 1
    scaler = MinMaxScaler()
    scaler.fit(X)
    X = scaler.transform(X)

    kmeans = KMeans(
        n_clusters=args['clusters'],
        init="random",
        max_iter=10000,
        random_state=args['random_state'],
        algorithm=args['algorithm'])
    kmeans.fit(X)

    df['cluster'] = kmeans.labels_
    df['cluster'] = df['cluster'].apply(str)
    df.drop(columns=['no_id'], axis=1, inplace=True)

    save_results(filename='clusterization',
                 df=df,
                 filepath=f'./data/users/{user}')

    print("Clusterization done!")
