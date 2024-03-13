import csv
import json

"""
Utility functions for saving data to different formats
"""
    
def save_json(data: dict, path: str ):
    """
    Save data to a json file with utf-8 encoding.

    Args:
        data (dict): dictionary to save
        filename (str): name of the file. Do not include the extension
        path (str, optional): path to save the file. Example: ./links. Do not include the extension
    """
    with open(f"{path}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    print(f"Saved to {path}.json")

def save_csv(data: dict, path: str):
    """
    Save data to a csv file with utf-8 encoding.

    Args:
        data (dict): dictionary to save
        path (str, optional): path to save the file. Example: ./links. Do not include the extension
    """
    with open(f"{path}.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        for key, value in data.items():
            writer.writerow([key, value])
    print(f"Saved to {path}.csv")
    
def save_txt(content: str, metadata: dict, path: str = "./"):
    """
    Saves string content to a txt file and metadata to a meta file.

    Args:
        content (str): content of the article
        metadata (dict): metadata of the article
        path (str): path to save the file
    """
    with open(f"{path}.txt", 'w', encoding='utf-8') as file:
        file.write(content)
    with open(f"{path}.meta", 'w', encoding='utf-8') as file:
        json.dump(metadata, file, ensure_ascii=False)