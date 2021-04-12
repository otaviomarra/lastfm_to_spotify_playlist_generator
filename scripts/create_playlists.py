import time
import json
import datetime
from math import ceil
from datetime import date, timedelta, datetime

import spotipy
import spotipy.util as util
import numpy as np
import pandas as pd
import requests_cache
import requests as re



df = pd.read_csv('../data/clusterization.csv')
df = df[['label', 'id']]
#Generate the spotify uris following their standardized pattern
df['uris'] = 'spotify:track:' + df['id']


# #### [get your token here](https://developer.spotify.com/console/post-playlist-tracks/?playlist_id=%7Bplaylist%7D&position=&uris=spotify%3Atrack%3A7uuWlqHI41LkdXn4pcqI1h%2Cspotify%3Atrack%3A15jdwHb5nOWJrxXvPavXTR%2Cspotify%3Atrack%3A2LwM4JgvJ3SiIaQOIXJT6n)

# In[72]:


#authentication. for now it is a manyally requst token but I'll come back to that later
access_token = 'BQA0P4vTq7_VpbAZMdd_xwrRY1-4_WuaxWYMPYkEID-nNf-3Tu7Dw_zpwZJn-aLB3vyKOGUAxpZOfcGy95MBN3GksyXwo3Ro7aoxIA58TMrq04GQdqWSzFu2Lp7fv_uxjCDKgIY-bkjKhpztJyTYeLIEKo0Rjo8Jv8kQG_kC8CP-CSl7CXZt61eVK5fqkPTP8iFA2MBL'
headers = {f'Content-Type":"application/json", "Authorization":"Bearer {access_token}'}
user_id = 'ommarra'


# ### Creating the playlists
# 
# **IMPORTANT:** the playlists should either be created at the same time or we'd need to manually create the playlists array with their ids
# If needed, you can manually delete the playlists on Spotify and then re-create them

# In[9]:


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
    #generate a dict with the labels and the playlist id - this will be used to add the songs later
    playlists[label] = r.json()['id']


# ### Adding songs to the playlists

# In[113]:


def add_songs_to_playlist(songs, playlist):
    """
    Makes the API request to add songs on an existing Spotify playlist
    Receives a string with all the songs uris on a csv format (up to 100 at a time) and the playlist id
    It works on batches of up to 100 songs at a single time

    Returns None
    """
    url = f'https://api.spotify.com/v1/playlists/{playlist}/tracks'
    data = json.dumps({ 'uris': songs })
    response = re.post(url=url, data=data, headers=headers)
    print(response.json())


# In[118]:


for key in playlists:
    playlist = playlists[key]
    #150 songs per playlist is a good starter. Later on I'd like to also limit the number of songs from the same artist
    tempdf = df[df['label'] == key].sample(150) 
    #break it even to post the ids in chunks (respecting the api limitation off batches of 100s)
    splits = ceil(len(tempdf)/100)
    chunks = np.array_split(tempdf, splits)
    #format and call the function to every chunk
    for i in range(len(chunks)):
        songs = chunks[i]['uris'].to_json(orient='records')
        add_songs_to_playlist(songs=json.loads(songs), playlist=playlist)        

