#!/usr/bin/env python
# coding: utf-8

# In[53]:


from datetime import date, datetime

import numpy as np
import pandas as pd
from pandasql import sqldf
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from pandas_profiling import ProfileReport
from sklearn.preprocessing import MinMaxScaler

pysqldf = lambda q: sqldf(q, globals())


# In[54]:


features = pd.read_csv('data/songs_features.csv')
played =  pd.read_csv('data/played_tracks.csv')
ids = pd.read_csv('data/spotify_tracks_ids.csv')


# In[55]:


q = """
SELECT p.artist, p.song_name, p.unix_timestamp, f.*
FROM played as p
LEFT JOIN ids as i on i.band_name = p.artist and i.song_name = p.song_name
LEFT JOIN features as f on f.id = i.sp_id
"""
raw = pysqldf(q)


# #### Organize the dataset

# In[56]:


#take a look at the NaNs first to be sure 
raw[raw['id'].isna() == False][['artist', 'song_name']].nunique()
#there are 1051 unique songs we couldn't find the id (17.4%)
##I'll find a way to deal with this another time


# In[57]:


#unix timestamp to readable datetime
raw['play_timestamp'] = pd.to_datetime(raw['unix_timestamp'], unit='s')
#drop the songs we couldn't find the spotify id
raw.dropna(inplace= True )
#drop some columns we won't need (or that I don't want to use as a feature)
raw.drop(columns = ['unix_timestamp', 'key', 'mode', 'speechiness', 'liveness', 'type', 'uri', 'track_href', 'analysis_url'], axis = 1, inplace  =True)


# Pandas profiling all the song features

# In[7]:


profile = ProfileReport(
    raw[['danceability', 'energy', 'loudness','acousticness', 'instrumentalness', 'valence', 'tempo', 'duration_ms','time_signature']], 
    title='Song features 2019',
    html={'style':{'full_width':True}})
profile.to_file('profiling.html')


# ## K-means

# In[ ]:


raw.groupby('id').count().describe()['play_timestamp']


# In[85]:


# Cleaning up a bit more so we can generate playlists only with songs often listened to
##I'd like to check the results considering only the songs that I've listened to more than once
q = """
with base as(
    SELECT DISTINCT id,
        danceability,
        energy,
        loudness,
        acousticness,
        instrumentalness,
        valence,
        tempo,
        COUNT(*) as count
    FROM raw
    GROUP BY 1,2,3,4,5,6,7,8)
SELECT * FROM base --WHERE count > 1
"""
kdf = pysqldf(q)


# In[86]:


#Visualizing all features distributions on scatterplots
fig = px.scatter_matrix(kdf.drop(columns = ["id", "count"],axis=1),
width=1200, height=1600)
fig.show()


# In[87]:


#Defining how many clusters would fit best for our data

X=kdf.drop(columns = ["id", "count"],axis=1)

#using StandardScaler to normalize allv alues between 0 and 1
scaler = MinMaxScaler()
scaler.fit(X)
X=scaler.transform(X)

#get the inertial value for 1-10 clusters
inertia = []
for i in range(1,11):
    kmeans = KMeans(
        n_clusters=i, init="k-means++",
        n_init=10,
        tol=1e-04, random_state=4
    )
    kmeans.fit(X)
    inertia.append(kmeans.inertia_)
#plot the chart so we can find the elbolw
fig = go.Figure(data=go.Scatter(x=np.arange(1,11),y=inertia))
fig.update_layout(title="Inertia vs Cluster Number",xaxis=dict(range=[0,11],title="Cluster Number"),
                  yaxis={'title':'Inertia'},
                 annotations=[
        dict(
            x=3,
            y=inertia[2],
            xref="x",
            yref="y",
            text="Elbow test for k-means",
            showarrow=True,
            arrowhead=7,
            ax=20,
            ay=-60
        )
    ])


# In[95]:


#implementing the k-means model
#I decided to go with 4. Whatever
kmeans = KMeans(
        n_clusters=4, 
        init="k-means++",
        n_init=10,
        max_iter=1000,
        tol=1e-04, 
        random_state=4)
kmeans.fit(X) #X from the above cell


# In[96]:


clusters=pd.DataFrame(X,columns=kdf.drop(columns=["id", 'count'],axis=1).columns)
clusters['label']=kmeans.labels_
polar=clusters.groupby("label").mean().reset_index()
polar=pd.melt(polar,id_vars=["label"])
fig = px.line_polar(polar, r="value", theta="variable", color="label", line_close=True, height=800,width=1400)
fig.show()


# In[97]:


clusters['id'] = kdf['id']
clusters.groupby('label').count()['id']


# ### Taking a look at the clusters generated

# In[114]:


q = """
SELECT DISTINCT c.label, p.artist, p.song_name
FROM played as p
LEFT JOIN ids as i on i.band_name = p.artist and i.song_name = p.song_name
LEFT JOIN clusters as c on c.id = i.sp_id
"""
tempdf = pysqldf(q)
for i in range(len(clusters['label'].unique())):
    print("Cluster ",clusters['label'].unique()[i].item())
    tempdf2 = tempdf[tempdf['label'] == clusters['label'].unique()[i].item()] 
    print(tempdf2.sample(25))
    print("\n")


# In[115]:


clusters.to_csv('../data/clusterization.csv', index=False)

