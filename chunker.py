import csv
from langchain_text_splitters import TokenTextSplitter

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

def chunk(dataset: list[list[str]], format:dict, index_of_description: str) -> list[list[str]]:
    """
    Chunks a dataset into by the different information and corresponding metadata.
    
    Args:
        dataset(list[list[[str]]): The CSV file we want to chunk, must contain a list of rows, each row containing a list of information
        format (dict): The way the metadata is stored in a particular CSV file, type_of_information:index (ie: {title:0, publication date:1, url:2})
        index_of_description (str): Index of where the information is in the CSV file
        
    Returns:
        list[list[str]]: List containing a chunk, each chunk has a text and its metadata.
    """
    
    for row in first_dataset: 
        metadata = create_metadata(row=row, format=format)
        textChunks = TokenTextSplitter(chunk_size=4096, chunk_overlap = 20).split_text(text=row[index_of_description])
        for text in textChunks:
            chunks.append([text, metadata])
    

if __name__ == "__main__":
    chunks = []
    
    first_dataset = parse_dataset("datasets\\Communiqués de presse\\Communiqués de presse (2023 à aujourd'hui).csv")
    chunk(dataset=first_dataset, format={"title":0,"publication date":1,"url":2,"district service":4,"source":5}, index_of_description=3)
