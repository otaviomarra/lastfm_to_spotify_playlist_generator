import argparse
from datetime import date, time
import os

parser = argparse.ArgumentParser()
parser.add_argument('start', type=str, 
                    help='Start date on YYYYMMDD format')
parser.add_argument('user', type=str, 
                    help='Your lastfm user name')
parser.add_argument('apikey', type=str, 
                    help='Your lastfm api key. Reffer to https://www.last.fm/api')
parser.add_argument('-p', '--path', type=str, 
                    help='Set the path to save de csv file. If empty, will save to [current_path]/data/')
parser.add_argument('-d', '--delete_cache', action='store_true', 
                    help='Will delete the cached requests at the end of execution (will make further executions slower)')
args = vars(parser.parse_args())
