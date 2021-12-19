import os
import sys
import time
import requests as re
import warnings
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

    stored_data = load_user_results(filename='lastfm_played_tracks',
                                    user=user)

    from_date = int(time.mktime(
        datetime.strptime(args['start'], '%Y%m%d').date().timetuple()))

    if stored_data is None:
        # No stored data. No need to update the from date: make requests from the start date argument
        pass
    else:
        # If there is stored data, we need to compare the dates and update the from_date, if needed
        max_date = stored_data['unix_timestamp'].max().item()

        if max_date > from_date:
            from_date = max_date
        elif max_date == from_date:
            pass
        elif max_date < from_date:
            # If from_date is bigger than the maximum stored date, completely overwrite the file and restart from the new selected date

            warnings.warn(
                "Warning: start date bigger than the maximum stored date. All existing data will be overwritten")
            print(
                f"Current maximum stored date is {datetime.utcfromtimestamp(max_date).strftime('%Y-%m-%d %H:%M:%S')}")
            print("If you want to cancel, exit the program now!!!")
            time.sleep(5)
            stored_data = None

    responses = []

    response = get_lastfm_tracks(
        from_date=from_date, api_key=api_key, user=user)

    append_results(response['track'])

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

        time.sleep(0.2)

        page = int(response['@attr']['page']) + 1

    # Save results on a csv file
    print(f'Saving csv results on data/users/{user}/lastfm_played_tracks.csv')

    responses_df = pd.DataFrame(data=responses, columns=[
        'artist', 'song', 'unix_timestamp'])

    if stored_data is None:
        pass
    else:
        responses_df = responses_df.append(stored_data, ignore_index=True)

    save_results(filename='lastfm_played_tracks',
                 df=responses_df,
                 filepath=f'./data/users/{user}')

    print('All good! Played tracks extracted from Lastfm')
