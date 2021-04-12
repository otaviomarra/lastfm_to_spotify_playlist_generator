#!/usr/bin/env python
# coding: utf-8

# We'll try to fetch the artists and tracks I listened to in a specific period from lastfm and see if we can encirh this info with spotify data (because it only allows to 50 last tracks in a beta api)
# After that we can try som simple ML models on it :D 

# In[1]:


import time
import json
from math import ceil
from datetime import date, timedelta, datetime

import numpy as np
import pandas as pd
import requests_cache
import requests as re


# ### Pre-work

# In[187]:


tracks = pd.read_csv('../data/played_tracks.csv')
tracks.drop(tracks.columns[2], axis = 1, inplace = True)
tracks = tracks.drop_duplicates()


# ## Spotify API
# 
# ### Get Song IDs

# In[188]:


#create a request cache
requests_cache.install_cache('../cache/track_features_cache')


# In[190]:


#define a function for the api request that returns the json response
def search_song_request(song_name, band_name):
    """
    Makes the search song api request that returns the json response
    Utilizes the song and band names as a paremeter to search for the song
    """
    r = re.get('https://api.spotify.com/v1/search?' + 'q=artist:' + band_name + '%20track:' + song_name + '&market:from_token' + '&type=track&limit=50&include_external=audio' , headers = headers)
    try:
        return r.json()['tracks']['items']
    except:
        return None

def get_song_id(song_name, band_name):
    """
    Makes the search song api request and iterate on the responde to get the song id
    """
    response = search_song_request(song_name, band_name)
    if response is not None:
        for i in range(len(response)):
            #there must be a better way of doing this byt it'll work for now: 
                #we iterate through the entire artist list - there is a lot of useless data in the response
            if response[i]['album']['artists'][0]['name'] == band_name:
                return response[i]['id']
            else:
                pass
    #if no returns, we could not find id, so it returns not_found
    return 'not_found'


# In[2]:


#Authentication - getting an access token
auth_response = re.post('https://accounts.spotify.com/api/token', {
    'grant_type': 'client_credentials',
    'client_id': '6cb782c1b0404843b3e5a06e8361cb6e',
    'client_secret': 'a32c28deab714fa89091395089cbca90',
})

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']

#create a header with the access token
headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}


# In[192]:


print("started api calls at", datetime.now())
tracks['sp_id'] = tracks.apply(lambda x: get_song_id(x['song_name'], x['band_name']), axis = 1)
print("done at", datetime.now())


# In[195]:


tracks['no_id'] = tracks['sp_id'].apply(lambda x: x == 'not_found')
tracks.groupby('no_id').count()['sp_id']


# In[197]:


tracks.to_csv('../data/spotify_tracks_ids.csv', index=False)


# ### Get Song Features

# In[4]:


#Since we can only get data for tracks with a Spotify ID
tracks = tracks[tracks['no_id']==False]


# In[5]:


def get_song_features(ids):
    """
    API request to get Spotify's song features from the Spotify track id
    Receives a string containing a list of spotify_ids on csv format (the api request works with up to 100 ids at a time)
    Returns a json file with all the song features for the ids
    """
    r = re.get('https://api.spotify.com/v1/audio-features?ids=' + ids, headers=headers)
    return r.json()


# In[6]:


#Create and empty DF to store the results
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
    'time_signature',]

song_features = pd.DataFrame(columns=cols)


# In[7]:


#we can make a single request with a csv of up to 100 song ids at once. So we break the dataframe into smaller lists to make multiple requests
splits = ceil(len(tracks)/100)
chunks = np.array_split(tracks, splits)

for i in range(len(chunks)):
    #transform the IDs from each chun into a csv list (string format) to be used at the api request
    song_ids = chunks[i]['sp_id'].to_string(header=False,index=False).replace('\n ',',').lstrip()   
    #make the api request
    r = get_song_features(song_ids)
    #normalize and append the reults to a final dataframe
    temp = pd.json_normalize(r['audio_features'])
    song_features = song_features.append(temp)

song_features.set_index('id', inplace=True)
song_features.to_csv('../data/songs_features.csv')

