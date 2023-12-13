# Spotify playlist generator from Lastfm

Generate spotify playlists based on your lastfm records. 
Recover your lastfm played tracks, clusterize them into different playlists with k-means and generate new playlists on Spotify on demand

<br>

## Installing / Getting started

Make sure all libraries from [requirements.txt](https://github.com/otaviomarra/lastfm_track_analysis/blob/main/requirements.txt) are installed

The project was written using Selenium with Firefox to open a browser window for the user to authentication. Make sure you have both Firefox and the [Geckodriver](https://github.com/mozilla/geckodriver) plugin installed. You can also change to another browser on the [utils/spotify_api.py](https://github.com/otaviomarra/lastfm_track_analysis/blob/main/utils/spotify_api.py#L293)

### Initial Configuration

You will need to have acces to both lastfm and spotify apis (check links below to get you api tokens)

**Lastfm API** : [Last.fm API account](https://www.last.fm/api)<br>
**Spotify** : [Spotify for developers](https://developer.spotify.com/) - log in with you Spotify account and create a new app

After that, create a `.env` file on root, following the example below:

```
LASTFM_USER = "username"
LASTFM_API_KEY = "apikey"
SPOTIFY_CLIENT_ID = "clientid"
SPOTIFY_CLIENT_SECRET = "clientsecret"
```
No need to worry with the Spotify's user authentication - it will be made via browser when needed

<br>

## Features

The project consists of four scripts, each one that can perform a specific step on generating the playlists.

For all extractions and data processing, a series of files will be stored under the `./data` folder. For last_fm records and clusterization the files are stores in a `/{user}` subfolder, with the authenticated Lastfm username. Track id and spotify features data is shared in between all user authentications to save on api execution.

### lastfm_extraction
**[LINK](https://github.com/otaviomarra/lastfm_track_analysis/blob/main/scripts/lastfm_extraction.py)**

Access the user's lastfm data and retrieve all scrobles from the starting date up until the current date.

#### Arguments
|Argument|Required|Description|
|---|---|---|
|start|YES|The initial date from when all scrobles will be collected on a YYYYMMDD format|

#### Utilization example: 
```
$ python3 lastfm_extraction.py 20200101
```

#### Output
`data/{user}/lastfm_played_tracks.csv` sample:
```
artist,song,unix_timestamp
The Beatles,Here Comes The Sun,1618922976
Cyndyi Lauper,Girls Just Want To Have Fun,1618853797
```

### spotify_extraction
**[LINK](https://github.com/otaviomarra/lastfm_track_analysis/blob/main/scripts/spotify_extraction.py)**

Collect all spotify data from the previously scrobled songs, searching for both Artist and Song name. It returns both the song spotify_id and the song features. If the song id was not found, it will return `not_found` instead of the song id hash

#### Output
`data/spotify_tracks_ids.csv` sample:
```
artist,song,sp_id,no_id
The Stooges,Tight Pants - Remastered Studio,2K9JdrobtGd4hQcxqiINXS,False
Neurosis,Fire is the End Lesson,29xUjsv0hjPjnBSw4fUqyi,False
Om,At Giza,not_found,True
Mac DeMarco,Still Together,2RLm6OrnjLuoyQEowCJ6QE,False
```
`data/spotify_songs_features.csv` sample:
```
danceability,energy,key,loudness,mode,speechiness,acousticness,instrumentalness,liveness,valence,tempo,type,id,uri,track_href,analysis_url,duration_ms,time_signature
0.21,0.744,1,-9.898,1,0.0386,0.000174,0.294,0.329,0.0631,130.866,audio_features,29xUjsv0hjPjnBSw4fUqyi,spotify:track:29xUjsv0hjPjnBSw4fUqyi,https://api.spotify.com/v1/tracks/29xUjsv0hjPjnBSw4fUqyi,https://api.spotify.com/v1/audio-analysis/29xUjsv0hjPjnBSw4fUqyi,414413,4
0.274,0.606,4,-6.493,1,0.03,0.00962,0.0264,0.115,0.685,77.336,audio_features,5HR0UqvkEL1KhvaRtQVXFr,spotify:track:5HR0UqvkEL1KhvaRtQVXFr,https://api.spotify.com/v1/tracks/5HR0UqvkEL1KhvaRtQVXFr,https://api.spotify.com/v1/audio-analysis/5HR0UqvkEL1KhvaRtQVXFr,256960,4
0.198,0.756,1,-7.04,1,0.0518,0.00229,0.715,0.16,0.246,121.924,audio_features,4SNVaP303lu2bU5GnT3nMm
```

### clusterization
**[LINK](https://github.com/otaviomarra/lastfm_track_analysis/blob/main/scripts/clusterization.py)**

Runs k-means clusterization to classify all songs based on its spotify features. Default setup considers only some of the features but it can be adjusted in the [script](https://github.com/otaviomarra/lastfm_track_analysis/blob/main/scripts/clusterization.py#L52) 

Note the [notebook version](https://github.com/otaviomarra/lastfm_track_analysis/blob/main/kmeans_clusters.ipynb) also exists and can be used as a reference work for feature selection and visualization and determining the number of clusters

#### Arguments

|Argument|Required|Description|
|---|---|---|
|clusters|YES|Number of clusters to be generated|
|random_state|NO|Your lucky number (random state for the Kmeans model). Default is 1|
|Algorithm|NO|Algorithm for the KMeans clusterization. Check the documentation for more info [here](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html). Default is auto.|

#### Utilization example: 
```
$ python3 clusterization.py 3 -random_state=4 --algorithm="full"
```
#### Output
`data/{user}/clusterization.csv` 

sample:
```
TBD
```

### create_playlists
**[LINK](https://github.com/otaviomarra/lastfm_track_analysis/blob/main/scripts/create_playlists.py)**

Opens a Firefox (or another browser of choosing) screen to authenticate into Spotify and generates the playlists according to the clusterized data.

#### Arguments:
|Argument|Required|Description|
|---|---|---|
|replace_playlists|NO|If declared, it will update the previously created playlists instead of creating new ones|
|lenght|NO|Total number of songs per playlist. Default is 150|

#### Utilization example: 
```
$ python3 create_playlists.py 3 --replace_playlists --lenght=200
```
#### Output:
The playlists will be generated on the authenticated user's Spotify account.


<br>

## Further Developing (or a list of possible to do's)

* Docker: Further development to allow te browser GUI to be opened (probably with a vnc) is still missing. Therefore, **the current Dockerfile is still not working**
* Unit tests: still need to be implemented
* Replace csv files with a more efficient storage solution
