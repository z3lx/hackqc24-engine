import csv
from langchain.schema.document import Document
import json
import web_scraper

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

def create_documents(dataset: list[list[str]], format:dict, index_of_description: int, save_as_file:bool, save_as_list:bool) -> list[Document]:
    """
    Creates a Document from for every row in a CSV dataset
    
    Args:
        dataset (list[list[[str]]): The CSV file we want to create Documents for, must contain a list of rows, each row containing a list of information
        format (dict): The way the metadata is stored in a particular CSV file, type_of_information:index (ie: {title:0, publication date:1, url:2})
        index_of_description (int): Index of where the information is in the CSV file
        save_as_file (boolean): Says if we want to write all the chunks as txt and json files, writes in "chunks" project directory.
        save_as_list (boolean): Says if we want to save all the chunks as a list of Documents in memory.
        
    Returns:
        list[Document]: A list of Documents if save_as_list is true, returns Nothing otherwise.
    """
    
    documents = []
    
    for index, row in enumerate(dataset): 
        metadata = create_metadata(row=row, format=format)
        page_content = row[index_of_description]
        if format["url"] is not None:
            index_of_url = format["url"]
            url = row[index_of_url]
            page_content += web_scraper.scrape_montreal(url)
        
        if save_as_file:
            with open(f"chunks/document{index}.txt", "w", encoding="utf-8") as f1:
                with open(f"chunks/document{index}.meta", "w", encoding="utf-8") as f2:
                    f1.write(page_content)
                    json.dump(metadata, f2, ensure_ascii=False)
                    print(f"Document {index+1}/{len(dataset)} created       {round(((index+1)/len(dataset) * 100), 2)}% Done")
                    
        if save_as_list:
            document = Document(page_content=page_content)
            document.metadata = metadata
            documents.append(document)
        
    if save_as_file:
        return documents
    return None
            