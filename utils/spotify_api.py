import os
import sys
import json
import base64
import time
from math import ceil

import numpy as np
import pandas as pd
import requests as re
from selenium import webdriver


class spotify_requests(object):
    """
    Spotify requests makes only general api requests to collect public data.
    It does not require user atuthentication
      since it doesn't makes changes or access user personal data
    """

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


class spotify_user_api(object):
    """
    Spotify user api for actions that
        requires user authentication (access and change on personal data)
    """

    def __init__(self, client_id: str, client_secret: str, redirect_uri='https://www.google.com', scope: str) -> object:
        self.client_id = client_id
        self.client_secret = client_secret
        # run the browser authentication and return the authorization code only
        authorization_code = authenticate_user(
            redirect_uri=redirect_uri, scope=scope)
        print("User authentication successful \n")
        self.access_token = get_access_token(
            authorization_code=authorization_code, redirect_uri=redirect_uri)
        self.user_id = get_user_id()

    def authenticate_user(self, redirect_uri: str, scope: str) -> str:
        """
        Open Firefox on Selenium to authenticate the Spotify user

        For now, it is required for the user to have both Firefox installed and the geckodriver on PATH 
            but in the future I'll think on a better solution for on Docker

        Returns the authentication code to be used on the second step of the verification (after user add credentials)
        """
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': scope
        }
        request_url = re.Request(
            'GET', 'https://accounts.spotify.com/authorize', params=params).prepare().url

        driver = webdriver.Firefox()  # yeah for now its firefox only
        driver.get(request_url)

        while not driver.current_url.startswith(self.redirect_uri):
            continue

        authorization_code = driver.current_url.split(
            '?')[1].replace('code=', '')

        return authorization_code

    def get_access_token(self, authorization_code: str, redirect_uri: str) -> str:
        # After user authentication, make a new request to refresh token
        auth_pass = self.client_id + ':' + self.client_secret
        b64_auth_pass = base64.b64encode(auth_pass.encode('utf-8')).decode()
        r = re.post(
            url='https://accounts.spotify.com/api/token',
            headers={'Authorization': f'Basic {b64_auth_pass}'},
            data={
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': redirect_uri, })

        if r.status_code == 200:
            return r.json()['access_token']
        else:
            print(
                f'!!!Error getting the access token after authentication!!! \n {r.json()}')
            sys.exit()

    def get_user_id(self) -> str:
        r = re.get(url='https://api.spotify.com/v1/me',
                   headers={'Authorization': f'Bearer {self.access_token}'})
        if r.status_code == 200:
            return r.json()['id']
        else:
            print(f'!!!Error retrieving the user id!!! \n {r.json()}')
            sys.exit()
