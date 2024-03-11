import csv
from langchain.schema.document import Document
import json
import scraper

def parse_dataset(dataset_path:str) -> list[list[str]]:
    """
    Parses a CSV dataset.
    
    Args:
        dataset_path(str): The project path to the dataset.
        
    Returns:
        list[list[str]]: The dataset as a list, each item is a row in the dataset, each row contains a list of information.
    """
    
    dataset = []
    with open(dataset_path, encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader) # Skip the first row, it only contains column titles
        for row in reader:
            dataset.append(row)
    
    return dataset

def create_metadata(row:list[str], format:dict) -> dict:
    """
    Creates the metadata for a specific row in a CSV file.
    
    Args:
        row (list[str]): The row we want to create metadata for.
        format (dict): The way the metadata is stored in a particular CSV file, type_of_information:row_index (ie: {title:0, publication date:1, url:2})
        
    Returns:
        dict: The metadata for the given row.
    """
    
    metadata = {}
    for type_of_information in format.keys():
        try:
            row_index = format[type_of_information]
            metadata[type_of_information] = row[row_index]
        except IndexError:
            metadata[type_of_information] = None
    
    return metadata

def createDocuments(title:str, dataset: list[list[str]], format:dict, index_of_description: int) -> None:
    """
    Creates a Document from for every row in a CSV dataset
    
    Args:
        title (str): Title of the dataset
        dataset (list[list[[str]]): The CSV file we want to create Documents for, must contain a list of rows, each row containing a list of information
        format (dict): The way the metadata is stored in a particular CSV file, type_of_information:index (ie: {title:0, publication date:1, url:2})
        index_of_description (int): Index of where the information is in the CSV file
    """
    documents = []
    
    for index, row in enumerate(dataset): 
        metadata = create_metadata(row=row, format=format)
        page_content = row[index_of_description]
        if format["url"] is not None:
            index_of_url = format["url"]
            url = row[index_of_url]
            page_content += scraper.scrape_montreal(url)
        with open(f"chunks/{title}{index}.txt", "w", encoding="utf-8") as f1:
            with open(f"chunks/{title}{index}.meta", "w", encoding="utf-8") as f2:
                f1.write(page_content)
                json.dump(metadata, f2, ensure_ascii=False)
                print(f"Document {index+1}/{len(dataset)} created       {round(((index+1)/len(dataset) * 100), 2)}% Done")
            