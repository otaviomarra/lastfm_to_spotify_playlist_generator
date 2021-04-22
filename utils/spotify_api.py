import os
import json
from math import ceil
import requests as re

import numpy as np
import pandas as pd


class spotify_requests(object):
    def __init__(self, client_id: str, client_secret: str) -> object:
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = self.get_headers()

    def get_headers(self):
        """
        Authenticate the spotify app to retrieve a client_secret and generate the headers

        Arguments:
            client_id (string): The spotify app client id

            client_secret (string): The spotify app client secret

        Returns: 
            The headers on a json format
        """

        auth_response = re.post('https://accounts.spotify.com/api/token', {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        })

        access_token = auth_response.json()['access_token']

        return {'Authorization': f'Bearer {access_token}'}

    def search_song(self, song_name: str, band_name: str) -> json:
        """
        Makes the search song api request that returns the json response

        Arguments:
            song_name (string): Name of the song

            band_name (string): Name of the band

        Returns:
            A json with the 50 first results for the band + song name search on spotify
        """
        r = re.get('https://api.spotify.com/v1/search?' + 'q=artist:' + band_name + '%20track:' +
                   song_name + '&market:from_token' + '&type=track&limit=50&include_external=audio', headers=self.headers)
        try:
            return r.json()['tracks']['items']
        except:
            return None

    def find_song_id(self, song_name: str, band_name: str) -> str:
        """
        Makes the search song api request and iterate on the responde to get the spotify song id

        Arguments:
            song_name (string): Name of the song

            band_name (string): Name of the band

        Returns
            The spotify song id for the song (or 'not_found' if we couldn't find it)
        """
        os.system('clear')
        print(f"Searching for song {song_name} by {band_name}")
        response = self.search_song(song_name, band_name)
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

    def get_songs_features(self, ids: pd.Series) -> pd.DataFrame:
        """
        API request to get Spotify's song features from the Spotify track id

        Argument:
            ids (series): A series of spotify_ids on csv format (the api request works with up to 100 ids at a time)

        Returns
            A json file with all the song features for the ids
        """
        song_features = pd.DataFrame(
            columns=['danceability',
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
                     'time_signature', ])

        splits = ceil(len(ids)/100)
        chunks = np.array_split(ids, splits)

        for i in range(len(chunks)):
            # transform the IDs from each chunk into a csv list (string format) to be used at the api request
            song_ids = chunks[i].to_string(
                header=False, index=False).replace('\n ', ',').lstrip()
            # make the api request
            r = re.get('https://api.spotify.com/v1/audio-features?ids=' +
                       song_ids, headers=self.headers).json()

            # normalize and append the results to a final dataframe
            temp = pd.json_normalize(r['audio_features'])
            song_features = song_features.append(temp)

        return song_features
