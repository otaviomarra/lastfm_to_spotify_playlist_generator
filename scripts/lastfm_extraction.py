import os
import sys
import time
import requests as re
from datetime import datetime

import argparse
import pandas as pd
from dotenv import load_dotenv

from utils.utils import save_results, load_user_results


def parse_args():
    """
    Parse arguments passed when calling the scripts

    Returns a dict with all the arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('user', type=str,
                        help='username for personal data')
    parser.add_argument('start', type=str,
                        help='Start date on YYYYMMDD format')
    return vars(parser.parse_args())


def append_results(response):
    """
    Iteration fuction to work on each request page.
    The input is the json from the API request,  
        Append the results to a final responses list with all the data necessary

    Returns None
    """

    for i in range(len(response)):
        # Tracks currently being played does not have the date attribute, so we should use the current unix timestampfor that
        if '@attr' in response[i]:
            if response[i]['@attr']['nowplaying'] == 'true':
                r = [response[i]['artist']['#text'], response[i]['name'],
                     int(time.mktime(datetime.now().timetuple()))]
                responses.append(r)
        else:
            r = [response[i]['artist']['#text'], response[i]
                 ['name'], response[i]['date']['uts']]
            responses.append(r)


def get_lastfm_tracks(from_date, api_key, user, page=1):
    """
    Makes the api request on the lastfm api to reurn a specific page of the last played tracks
        If no pagination value is passed, it will make the request for the first page

    If anything wrong happens on the request, it will print the error status_code and stop the script execution

    Returns the played tracks from said page a json format
    """

    response = re.get(
        url='http://ws.audioscrobbler.com/2.0/',
        headers={'user-agent': 'my_played_tracks'},
        params={
            'method': 'user.getrecenttracks',
            'limit': 200,
            'api_key': api_key,
            'format': 'json',
            'user': user,
            'extended': 0,
            'from': from_date,
            'page': page
        }
    )

    if response.status_code == 200:
        return response.json()['recenttracks']
    else:
        raise Exception(f'ERROR! status_code = , {response.status_code}')


if __name__ == "__main__":

    # Get all env variables
    load_dotenv()
    user = os.environ.get("LASTFM_USER")
    api_key = os.environ.get("LASTFM_API_KEY")

    args = parse_args()

    stored_data = load_user_results(
        filename='lastfm_played_tracks', user=args['user'])

    if stored_data == False:
        # No stored data. Make requests from the stated start date
        from_date = int(time.mktime(
            datetime.strptime(args['start'], '%Y%m%d').date().timetuple()))
    else:
        # There is stored data. Only make requests from the maximum date onwards
        # If the stated start date is bigger than the maximum stored date, it will completely overwrite the file
        from_date = max(stored_data['unix_timestamp'].max(),
                        int(time.mktime(datetime.strptime(args['start'], '%Y%m%d').date().timetuple())))

    responses = []

    response = get_lastfm_tracks(
        from_date=from_date, api_key=api_key, user=user)

    append_results(response['track'])

    # If not cached, sleep to keep the api requests per second low
    if not getattr(response, 'from_cache', False):
        print('no cache')
        time.sleep(0.2)

    total_pages = int(response['@attr']['totalPages'])
    page = int(response['@attr']['page']) + 1

    # Loop through all other pages
    while page <= total_pages:
        os.system('clear')
        print("requesting page", page, "from", total_pages, "pages")

        response = get_lastfm_tracks(
            from_date=from_date, api_key=api_key, user=user, page=page)

        append_results(response['track'])

        # If not cached, sleep to keep the api requests per second low
        if not getattr(response, 'from_cache', False):
            time.sleep(0.2)

        page = int(response['@attr']['page']) + 1

    # Save results on a csv file
    print('Saving csv results on data/lastfm_played_tracks.csv')

    responses_df = pd.DataFrame(data=responses, columns=[
                                'artist', 'song', 'unix_timestamp'])
    save_results(filename='lastfm_played_tracks', df=responses_df)

    if args['delete_cache'] is True:
        remove_cache(filename='get_recent_tracks_cache')

    print('All good! Played tracks extracted from Lastfm user')
