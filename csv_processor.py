import csv
from langchain.schema.document import Document
import web_scraper
from utils.document import save_documents

def parse_csv_dataset(dataset_path:str) -> list[list[str]]:
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

def create_csv_metadata(row:list[str], format:dict) -> dict:
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

def create_documents_from_csv(dataset: list[list[str]], format: dict, index_of_description: int, save_path: str = "chunks") -> list[Document]:
    """
    Creates a Document for every row in a CSV dataset
    
    Args:
        dataset (list[list[[str]]): The CSV file we want to create Documents for, must contain a list of rows, each row containing a list of information
        format (dict): The way the metadata is stored in a particular CSV file: type_of_information:index (ie: {title:0, publication date:1, url:2})
        index_of_description (int): Index of where the information is in the CSV file.
        save_path (str): Directory where we want to save the documents (txt/meta files). If none, document's won't be saved. Defaults to "chunks"
        
    Returns:
        list[Document]: A list of Documents created from the CSV file.
    """
    
    documents = []
    
    for row in dataset: 
        # If the csv contains a url source, create Document by scraping it
        
        index_of_url = format["url"]
        url = row[index_of_url]
        print(f"Scraping {url}")
        if url.startswith("https://montreal.ca"):
            document = web_scraper.scrape_montreal(url)
        elif url.startswith("https://quebec.ca"):
            document = web_scraper.scrape_quebec(url)
        else:
            print("This Domain is not supported at the moment")
            metadata = create_csv_metadata(row, format)
            page_content = row[index_of_description]
            document = Document(page_content=page_content, metadata=metadata)
                
        documents.append(document)
        
    if save_path is not None:
        save_documents(save_path, documents, None)
        
    return documents


