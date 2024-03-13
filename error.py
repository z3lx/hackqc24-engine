"""
This module contains a wrapper function to handle errors related to requests while running the function.
"""

import requests
import time

def error_wrapper(link: str, callback: callable, retries: int = 5, retry_time: int = 5, **kwargs):
    """
    Wrapper function to handle errors related to requests while running the function.

    Args:
        func (Function): a function that takes in a response object and returns a value
        url (str): url of the webpage
        retry_time (int, optional): time in seconds to wait before retrying. Defaults to 5 seconds.
        retries (int, optional): number of retries. Defaults to 5.
        **kwargs: keyword arguments to be passed to the callback function

    Returns:
        Any | None: returns the value returned by the callback function or None if an error occurs
    """
    try:
        response = requests.get(link)
        if response.status_code == 200:
            return callback(response, **kwargs)
        else:
            print(f"Failed to retrieve {link}. Status code:", response.status_code)
            for retry in range(retries):
                print(f"Retrying in {retry_time} seconds...")
                print(f"{retries - retry} retrie(s) left.")
                time.sleep(retry_time)
                response = requests.get(link)
                if response.status_code == 200:
                    return callback(response, **kwargs)
        print(f"Couldn't retrieve {link}") 
        return None
    except Exception as e:
        print(f"Error occurred while running {callback.__name__}")
        print("Error:", e)
        return None