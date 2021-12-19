import warnings

import argparse
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

from utils.utils import save_results, load_results


def parse_args():
    """
    Parse arguments passed when calling the scripts

    Returns a dict with all the arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('clusters', type=int,
                        help='Number of clusters to be generated')
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

    # Remove features not bo be used
    df.drop(columns=['speechiness', 'liveness', 'danceability'],
            axis=1,
            inplace=True)

    # Removing the columns not to be used on the clusterization
    # Normalized to all feature values between 0 and 1
    X = df.drop(columns=['artist', 'song', 'id', 'duration_ms',
                'time_signature', 'no_id', 'tempo'], axis=1)
    scaler = MinMaxScaler()
    scaler.fit(X)
    X = scaler.transform(X)

    kmeans = KMeans(
        n_clusters=args['clusters'],
        init="random",
        max_iter=10000,
        random_state=4)
    kmeans.fit(X)

    df['cluster'] = kmeans.labels_
    df['cluster'] = df['cluster'].apply(str)
    df.drop(columns=['no_id'], axis=1, inplace=True)

    save_results(filename='clusterization',
                 df=df,
                 filepath=f'./data/users/{user}')

    print("Clusterization done!")
