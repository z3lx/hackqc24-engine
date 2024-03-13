import pandas as pd
import json

"""
Utility functions for saving data to different formats
"""
    
def save_json(data: dict, filename: str , dir: str = ""):
    """
    Save data to a json file with utf-8 encoding.

    Args:
        data (dict): dictionary to save
        filename (str): name of the file. Do not include the extension
        dir (str, optional): directory to save the file. Defaults to "".
    """
    with open(f"{dir}{filename}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    print(f"Saved to {dir}{filename}.json")

#@TODO: Add support for csv. The function below is broken
def save_csv(self, data: dict, filename: str, dir: str = ""):
    df = pd.DataFrame(data)
    df.to_csv(f"{dir}{filename}.csv", index=False, encoding="utf-8")
    print(f"Saved to {dir}{filename}.csv")
    
def load_json(filename: str, dir: str = "") -> dict:
    """
    Load a json file

    Args:
        filename (str): name of the file
        dir (str, optional): directory of the file. Defaults to "".

    Returns:
        dict: loaded data
    """
    with open(f"{dir}{filename}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

def load_csv(filename: str, dir: str = "") -> pd.DataFrame:
    """
    Load a csv file

    Args:
        filename (str): name of the file
        dir (str, optional): directory of the file. Defaults to "".

    Returns:
        pd.DataFrame: loaded data
    """
    return pd.read_csv(f"{dir}{filename}.csv", encoding="utf-8")
