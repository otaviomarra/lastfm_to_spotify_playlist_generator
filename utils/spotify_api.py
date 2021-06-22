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


def api_call(func):
    """
    This is just a wrapper for the api requests.
        In case the request is good, it will return the api response

        If we get an internal server error or exceed the api limits, it will wait for 5 seconds and retry (up to 8 times)

        If we get another error, raises an exception and prints the response error

        More info: https://developer.spotify.com/documentation/web-api/
    """
    def wrapper(*args, **kwargs):
        attempt = 1
        while attempt <= 8:
            r = func(*args, **kwargs)
            if r.status_code in [200, 201, 202, 204]:
                return r
            elif r.status_code in [429, 500]:
                time.sleep(5)
                print(
                    f'Attempt number {attempt} with status code {r.status_code}. Retrying...')
                attempt += 1
                continue
            else:
                raise Exception(
                    f'Error: Bad api call. Please try again. \n Response: \n {r}')
    return wrapper


@api_call
def get_request(*args, **kwargs):
    """
    Execute requests.get using the @api_call decorator
    """
    r = re.get(*args, **kwargs)
    return r


@api_call
def post_request(*args, **kwargs):
    """
    Execute requests.post using the @api_call decorator
    """
    r = re.post(*args, **kwargs)
    return r


@api_call
def delete_request(*args, **kwargs):
    """
    Execute requests.delete using the @api_call decorator
    """
    r = re.delete(*args, **kwargs)
    return r


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

    def __str__(self):
        return f"Spotify App client id {self.client_id}"

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
        r = get_request(url='https://api.spotify.com/v1/search?' + 'q=artist:' + band_name + '%20track:' +
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
            r = get_request(url='https://api.spotify.com/v1/audio-features?ids=' +
                            song_ids, headers=self.headers).json()

            # normalize and append the results to a final dataframe
            temp = pd.json_normalize(r['audio_features'])
            song_features = song_features.append(temp)

        return song_features


class spotify_user_api(object):
    """
    Spotify user api for actions that requires user authentication (access and change on personal data)

    Variables:
        client_id: the app client id

        client_secret: the app client secret

        scope: scope to be granted access to on the authentication
            It defined to what we will have access to
            More than one scope can be used separated by simple space ("scope1 scope2 scope3")

        access_token: the tokne generated after authentication, to be used on the API

        user_id: spotify user id. it will be used to generate the api endpoints

        headers: header with the access token, to be used on all requests made on the user api
    """

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scope: str) -> object:
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        # run the browser authentication and return the authorization code only
        authorization_code = self.authenticate_user(
            redirect_uri=redirect_uri, scope=scope)
        print("User authentication successful \n")
        self.access_token = self.get_access_token(
            authorization_code=authorization_code, redirect_uri=redirect_uri)
        self.headers = self.get_headers()
        self.user_id = self.get_user_id()

    def __str__(self):
        return f"Authenticated on user {self.user_id} with Scope {self.scope}. Spotify App client id {self.client_id}"

    def authenticate_user(self, redirect_uri: str) -> str:
        """
        Opens Firefox on Selenium to authenticate the Spotify user
        For now, it is required for the user to have both Firefox installed and the geckodriver on PATH
            but in the future I'll think on a better solution for on Docker
        Returns the authentication code to be used on the second step of the verification (refresh token)

        Arguments:
            redirect_uri (string): the redirect uri used on the authentication process
                Mind that this should be exactly the same as used on the following token refresh and also to be registered on the web app

        Returns the authorization_code (string)
        """
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': self.scope
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
        """
        The access token to be used on the api
        After user authentication return an authorization code, we need to make a new request to refresh token

        Arguments:
            authorization_code (string): the authorization code generated on the user authentication

            redirect_uri (string): the redirect uri used on the authentication process
                Mind that this should be exactly the same as used on the authentication and also to be registered on the web app

        Returns the access_token (string)
        """
        auth_pass = self.client_id + ':' + self.client_secret
        b64_auth_pass = base64.b64encode(auth_pass.encode('utf-8')).decode()
        r = post_request(
            url='https://accounts.spotify.com/api/token',
            headers={'Authorization': f'Basic {b64_auth_pass}'},
            data={
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': redirect_uri, })

        return r.json()['access_token']

    def get_headers(self):
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.access_token}"}

    def get_user_id(self) -> str:
        """
        Get the user id to be used on the following post requests

        Returns the user_id (string)
        """
        # r = get_request(url='https://api.spotify.com/v1/me',
        #                headers={'Authorization': f'Bearer {self.access_token}'})

        r = get_request(url='https://api.spotify.com/v1/me',
                        headers=self.headers)

        return r.json()['id']

    def create_playlist(self, name: str, description: str, public=True, collaborative=False) -> None:
        """
        Create a playlist on Spotify

        Arguments:
            name (string):name of the playlist

            description (string): playlist description. the function defaults to empty if no input

            public (bool): if the playlist will be public or private
                In order to set playlist to private, the playlist-modify-private scope should be granted.
                If that's not the case, an error will be raised

            collaborative (bool): if the playlist is collaborative or not.
                The spotify api defaults it to False.
                To create collaborative playlists you must have granted playlist-modify-private and playlist-modify-public scopes.
                Collaborative playlists will always be private (public = False)

        Returns None
        """

        if 'playlist-modify-private' not in self.scope and public == False:
            raise Exception('Wrong scope: cannot create private playlist')
        elif collaborative == True and public == True:
            raise Exception('Collaborative playlists cannot be public')
        else:
            pass

        request_body = json.dumps({
            "name": name,
            "description": description,
            "public": public,
            "collaborative": collaborative
        })

        r = post_request(url=f'https://api.spotify.com/v1/users/{self.user_id}/playlists',
                         data=request_body,
                         headers=self.headers)

    def add_song_to_playlist(self, songs: str or list, playlist: str) -> None:
        """
        Makes the API request to add songs on an existing Spotify playlist

        Arguments:
            songs (string, list): all the songs to be added to the playlist in a csv string or list format
                It can receive either song ids or song uris or both of them at the same time
                Up to 100 at a time can be added to the playlist. If more than 100 songs uris are passed, an Exception will be raised

            playlist (string): the playlist id where the songs should be added

        Returns None
        """

        if type(songs) == str:
            songs = songs.split(',')
        elif type(songs) == list:
            pass
        else:
            raise Exception(
                "Wrong dataype input for songs. Use either string or list")

        assert len(
            songs) <= 100, "No more than 100 song uris at a time can be passed"

        songs = ["spotify:track:" + song_id
                 if "spotify:track:" not in song_id else song_id for song_id in song_uris]
        songs = json.dumps({'uris': songs})
        # should receive a string with plain csvs or a list

        r = post_request(url=f'https://api.spotify.com/v1/playlists/{playlist}/tracks',
                         data=songs,
                         headers=self.headers)

    def get_playlist_songs(self, playlist: str) -> list:
        """
        Get all song uris from a specified playlist.
        Mind that different scopes might be needed, depending on the playlist to be either public or private

        Arguments:
            playlist (string): the playlist id where the songs should be added

        Returns a list of all song uris (uri format: "spotiy:track:{song_id}")
        """

        r = re.get(url=f'https://api.spotify.com/v1/playlists/{playlist}/tracks?fields=total',
                   headers=self.headers)

        total_songs = r.json()['total']

        # first request
        r = get_request(url=f'https://api.spotify.com/v1/playlists/{playlist}/tracks?fields=items(track(uri))',
                            headers=self.headers)

        song_uris = [r.json()['items'][i]['track']['uri']
                     for i in range(len(r.json()['items']))]

        # iterate through the following requests
        offset = 100  # maximum of 100 song ids per request
        while offset < total_songs:
            r = get_request(url=f'https://api.spotify.com/v1/playlists/{playlist}/tracks?offset={offset}&fields=items(track(uri))',
                            headers=self.headers)

            temp_list = [r.json()['items'][i]['track']['uri']
                         for i in range(len(r.json()['items']))]
            song_uris = song_uris + temp_list
            offset += 100

        return song_uris

    def delete_playlist_songs(self, playlist: str, songs: list or str = None, delete_all: bool = False):
        """
        Makes the API request to add songs on an existing Spotify playlist

        Arguments:
            songs (string, list): all the songs to be deleted from the playlist in a csv string or list format
                It can receive either song ids or song uris or both of them at the same time
                Up to 100 at a time can be added to the playlist. If more than 100 songs uris are passed, an Exception will be raised

            playlist (string): the playlist id where the songs should be added

            delete_all (bool): if True, the code WILL IGNORE the list of song uris passed and will delete all songs from the playlist

        Returns None
        """

        if delete_all == True:
            songs = self.get_playlist_songs(playlist=playlist)
        elif type(songs) == str & delete_all == False:
            songs = songs.split(',')
        elif type(songs) == list & delete_all == False:
            pass
        else:
            raise Exception(
                "Wrong dataype input for songs. Use either string or list")

        songs = ["spotify:track:" + song_id
                 if "spotify:track:" not in song_id else song_id for song_id in song_uris]
        songs = [{"uri": uri} for uri in songs]
        songs = json.dumps({"tracks": songs})

        delete_request(url=f'https://api.spotify.com/v1/playlists/{playlist}/tracks',
                       data=songs,
                       headers=self.headers)
