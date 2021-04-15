import pathlib
import pandas as pd
import requests_cache


def initiate_cache(filename, relative_path='./cache'):
    """
    Initiates the sqlite cache for the api requests

    Variables:
        filename (string): name of the cache file to be created without the extension

        relative_path (string): relative path where the cached file will be created. 
            If the relative path stated does not exist, it will create the folder.

    Returns None
    """
    if not pathlib.Path(relative_path).is_dir():
        pathlib.Path(relative_path).mkdir()

    file_path = relative_path + '/' + filename
    requests_cache.install_cache(file_path)


def remove_cache(filename, relative_path='./cache'):
    """
    Removes the cached sqlite from the api requests

    Variables:
        filename (string): name of the cache file to be created without the extension

        relative_path (string): relative path where the cached file will be created. 
            If the folder on the relative path stated is empty it will also delete the folder

    Returns None
    """

    print('Removing ', filename, ' cache')

    file_path = relative_path + '/' + filename + '.sqlite'
    pathlib.Path(file_path).unlink()

    try:
        pathlib.Path(relative_path).rmdir()
    except OSError:
        pass


def save_results(filename, df, filepath='./data'):
    """
    Saves the results for th api request. If the foler does not exist, creates it first
    Mind that the file will be saved without the index

    Arguments:
        filename (string): name of the csvfile to be saved

        df (dataframe): dataframe to be saved as a csv file

        columns: 

        relative_path (string): relative path where the cached file will be created. 
            If the relative path stated does not exist, it will create the folder.

    Returns None
    """

    if not pathlib.Path(filepath).is_dir():
        pathlib.Path(filepath).mkdir()

    savepath = filepath + '/' + filename + '.csv'
    df.to_csv(savepath, index=False)
