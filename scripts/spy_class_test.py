from utils.spotify_api import spotify_session
import pandas as pd

session = spotify_session(client_id='6cb782c1b0404843b3e5a06e8361cb6e',
                          client_secret='a32c28deab714fa89091395089cbca90')


_id = session.find_song_id(song_name='The Fall', band_name='Cult Of Luna')

print(_id)

ids = pd.Series(data=['2hb90lgdGzfU2B01s2ItnU', '79FRd4gq3o7yXSexLVsAFh'])

df = session.get_song_features(ids=ids)

print(df)
