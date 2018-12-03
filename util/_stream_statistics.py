"""
Show statistics of a csv file.
The expected contents of the file is as '_prepare_offline_data.py's
output csv file.
"""


import glob
import logging
import pandas as pd


def analyze(file_path=None):
    """analyze
    Analyze streams from csv files.
    It shows

    Parameters
    ----------
    file_path: str (default=None)
        path to the target csv file. 
        If None, the first csv file under './data/csv_data/' will be selected.

    Returns
    -------

    """
    if not file_path:
        pass
    else:
        pass
    
    pass

if __name__ == '__main__':
    analyze()