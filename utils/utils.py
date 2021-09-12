import sys
import pathlib
import pandas as pd
#import requests_cache


# def initiate_cache(filename: str, relative_path='./cache') -> None:
#    """
#    Initiates the sqlite cache for the api requests
#
#    Variables:
#        filename (string): name of the cache file to be created without the extension
#
#        relative_path (string): relative path where the cached file will be created.
#            If the relative path stated does not exist, it will create the folder.
#
#    Returns None
#    """
#    if not pathlib.Path(relative_path).is_dir():
#        pathlib.Path(relative_path).mkdir()
#
#    file_path = relative_path + '/' + filename
#    requests_cache.install_cache(file_path)
#
#
# def remove_cache(filename: str, relative_path='./cache') -> None:
#    """
#    Removes the cached sqlite from the api requests
#
#    Variables:
#        filename (string): name of the cache file to be created without the extension
#
#        relative_path (string): relative path where the cached file will be created.
#            If the folder on the relative path stated is empty it will also delete the folder
#
#    Returns None
#    """
#
#    print('Removing ', filename, ' cache')
#
#    file_path = relative_path + '/' + filename + '.sqlite'
#    pathlib.Path(file_path).unlink()
#
#    try:
#        pathlib.Path(relative_path).rmdir()
#    except OSError:
#        pass


def save_results(filename: str, df: pd.DataFrame, filepath='./data') -> None:
    """
    Saves the results for th api request. If the folder does not exist, creates it first
    Mind that the file will be saved without the index

    Arguments:
        filename (string): name of the csv file to be saved (without the extension)

        df (dataframe): dataframe to be saved as a csv file

        filepath (string): relative path where the results should be stored 
            If the relative path stated does not exist, it will create the folder.

    Returns None
    """

    if not pathlib.Path(filepath).is_dir():
        pathlib.Path(filepath).mkdir()

    savepath = filepath + '/' + filename + '.csv'
    df.to_csv(savepath, index=False)


def load_results(filename: str, filepath: str = './data') -> pd.DataFrame:
    """
    Load csv files.

    Arguments:
        filename (string): name of the csv file to be loaded (without the extension)

        filepath (string): relative path to the folder where the csv file is stored

    Returns:
        A Pandas dataframe of the loaded csv file. If the file doesn't exist, returns None
    """

    loadpath = filepath + '/' + filename + '.csv'
    if pathlib.Path(loadpath).is_file():
        try:
            return pd.read_csv(loadpath)
        except Exception as e:
            print(e)
            sys.exit()
    else:
        return None


def load_user_results(filename: str, user: str, filepath: str = './data') -> pd.DataFrame:
    """
    Load personal user information.

    Arguments:
        filename (string): name of the csv file to be loaded (without the extension)

        user (string): username in which the data is stored

        filepath (string): relative path to the folder where the csv file is stored

    Returns:
        A Pandas dataframe of the loaded csv file. If the file doesn't exists, returns None
    """

    filepath = filepath + '/users/' + user

    if pathlib.Path(filepath + '/' + filename + '.csv').is_file():
        return load_results(filename=filename, filepath=filepath)
    else:
        print(
            f"WARNING: No personal {filename} data found for {user}")
        return None
