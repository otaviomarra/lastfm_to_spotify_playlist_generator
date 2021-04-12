import time
import requests as re
from datetime import date, time

import argparse
import requests_cache
from IPython.core.display import clear_output


def structure_table(artist, song, date):
    """
    Receive all attributes from the json and structure them on a list following the desired table format
    
    Returns a list with the values of one row
    """
    arr  = [artist, song, date]
    return arr

def page_iterator(response):
    """
    Iteration fuction to work on each request page.
    The input is the json from the API request,  
        runs the structure_table function and append it to a final response list

    Returns None
    """
    for i in range(len(response)):
        r = structure_table(response[i]['artist']['#text'],response[i]['name'], response[i]['mbid'], response[i]['date']['uts'])
        responses.append(r)

def parse_args():
    

if __name__ == "__main__":

    
    requests_cache.install_cache('../cache/get_recent_tracks_cache')

    from_date = int(time.mktime(datetime.date(2021,1,1).timetuple()))

    responses = []
    headers = {'user-agent': 'my_played_tracks'}

    #First request
    params = {
            'method': 'user.getrecenttracks',
            'limit': 200,
            'api_key': 'cf786f78db52a45f40f6e7b573b7d211',
            'format': 'json',
            'user': 'ommarra',
            'extended': 0,
            'from':from_date,
            'page': 1
            }

    response = re.get('http://ws.audioscrobbler.com/2.0/', headers = headers, params = params)
    response = response.json()['recenttracks']
    page_iterator(response['track'])

    #Get the total pages
    total_pages = int(response['@attr']['totalPages'])
    page = int(response['@attr']['page']) + 1


    #Loop through all other pages
    while page <= total_pages:
        clear_output(wait=True)
        print("requesting page", page, "from", total_pages, "pages")

        params = {
            'method': 'user.getrecenttracks',
            'limit': 200,
            'api_key': 'cf786f78db52a45f40f6e7b573b7d211',
            'format': 'json',
            'user': 'ommarra',
            'extended': 0,
            'from': _from,
            'page': page
            }

        response = re.get('http://ws.audioscrobbler.com/2.0/', headers = headers, params = params)
        
        if response.status_code == 200:
            response = response.json()['recenttracks']
            page_iterator(response['track'])
        else:
            print("error:", response.status_code)
            break
        
        # If not cached, sleep to keep the api requests per second low
        if not getattr(response, 'from_cache', False):
            time.sleep(0.2)

        page = int(response['@attr']['page']) + 1


    pd.DataFrame(data=responses, columns=['artist', 'song', 'unix_timestamp']).to_csv("../data/played_tracks.csv", index = False)

