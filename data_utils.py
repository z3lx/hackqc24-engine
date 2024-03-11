import pandas as pd
import json

"""
Utility functions for saving data to different formats
"""
    
def save_to_json(data: dict, filename: str , dir: str = ""):
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
def save_to_csv(self, data: dict, filename: str, dir: str = ""):
    df = pd.DataFrame(data)
    df.to_csv(f"{dir}{filename}.csv", index=False, encoding="utf-8")
    print(f"Saved to {dir}{filename}.csv")