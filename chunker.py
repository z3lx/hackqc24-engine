import csv
from langchain_text_splitters import TokenTextSplitter
from langchain.schema.document import Document
import json

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

def chunkAsDocument(dataset: list[list[str]], format:dict, index_of_description: int) -> list[Document]:
    """
    Chunks a dataset by the different information and corresponding metadata into a list of Document objects.
    
    Args:
        dataset(list[list[[str]]): The CSV file we want to chunk, must contain a list of rows, each row containing a list of information
        format (dict): The way the metadata is stored in a particular CSV file, type_of_information:index (ie: {title:0, publication date:1, url:2})
        index_of_description (int): Index of where the information is in the CSV file
        
    Return:
        list[Document]: List of Document objects representing the different chunks.
    """
    documents = []
    
    for row in dataset: 
        metadata = create_metadata(row=row, format=format)
        text_chunks = TokenTextSplitter(chunk_size=4096, chunk_overlap = 20).split_text(text=row[index_of_description])
        for text in text_chunks:
            documents.append(Document(page_content=text, metadata=metadata))
            
    return documents
    
def chunkAsFile(title: str, dataset: list[list[str]], format:dict, index_of_description: int) -> None:
    """
    Chunks a dataset by the different information and corresponding metadata and write them into 2 separate files (ie: chunk1.txt, chunk1.meta (JSON)).
    
    Args:
        title (str): Title of the dataset.
        dataset (list[list[[str]]): The CSV file we want to chunk, must contain a list of rows, each row containing a list of information
        format (dict): The way the metadata is stored in a particular CSV file, type_of_information:index (ie: {title:0, publication date:1, url:2})
        index_of_description (int): Index of where the information is in the CSV file
    """
    for index, row in enumerate(dataset):
        with open(f"chunks\\{title}{index}.txt", "w", encoding="utf-8") as f1:
            with open(f"chunks\\{title}{index}.meta", "w", encoding="utf-8") as f2:
                metadata = create_metadata(row=row, format=format)
                text_chunks = TokenTextSplitter(chunk_size=4096, chunk_overlap = 20).split_text(text=row[index_of_description])
                for text in text_chunks:
                    f1.write(text) # write page content as txt file
                    json.dump(metadata, f2, ensure_ascii=False) # write metadeta as JSON
                    index += 1 # A row can have multiple chunks
    

if __name__ == "__main__":
    first_dataset = parse_dataset("datasets\\Communiqués de presse\\Communiqués de presse (2023 à aujourd'hui).csv")
    documents = chunkAsDocument(dataset=first_dataset, format={"title":0,"publication date":1,"url":2,"district service":4,"source":5}, index_of_description=3)
    chunkAsFile(title="vmtl-communique-presse", dataset=first_dataset,format={"title":0,"publication date":1,"url":2,"district service":4,"source":5}, index_of_description=3) # Dataset title name is hard coded into function parameter

    second_dataset = parse_dataset("datasets\\Avis et alertes\\Avis et alertes.csv")
    documents = chunkAsDocument(dataset=first_dataset, format={"title":0,"start date":1,"end date":2,"type":4,"service":5,"url":6}, index_of_description=None)
    chunkAsFile(title="vmtl-communique-presse", dataset=first_dataset,format={"title":0,"publication date":1,"url":2,"district service":4,"source":5}, index_of_description=3)