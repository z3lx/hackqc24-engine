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

def create_documents_from_csv(dataset: list[list[str]], format:dict, index_of_description: int, save_path:str = "chunks", save_as_list:bool = True) -> list[Document]:
    """
    Creates a Document for every row in a CSV dataset
    
    Args:
        dataset (list[list[[str]]): The CSV file we want to create Documents for, must contain a list of rows, each row containing a list of information
        format (dict): The way the metadata is stored in a particular CSV file: type_of_information:index (ie: {title:0, publication date:1, url:2})
        index_of_description (int): Index of where the information is in the CSV file.
        save_path (str): Directory where we want to save the documents (txt/meta files). If none, document's won't be saved. Defaults to "chunks"
        save_as_list (boolean): If we want to save all the chunks as a list of Documents in memory. Defaults to True
        
    Returns:
        list[Document]: A list of Documents if save_as_list is true, returns Nothing otherwise.
    """
    
    documents = []
    
    for index, row in enumerate(dataset): 
        # If the csv contains a url source, create Document by scraping it
        try:
            index_of_url = format["url"]
            url = row[index_of_url]
            print(f"Scarping {url}")
            if url.startswith("https://montreal.ca"):
                document = web_scraper.scrape_montreal(url)
                continue
            elif url.startswith("https://quebec.ca"):
                document = web_scraper.scrape_quebec(url)
                continue
            else:
                print("This Domain is not supported at the moment")
                raise KeyError
                
        # Create Document using csv otherwise
        except KeyError:
            metadata = create_csv_metadata(row, format)
            page_content = row[index_of_description]
            document = Document(page_content=page_content, metadata=metadata)

        documents.append(document)
        
    if save_path is not None:
        save_documents("chunks", documents, source_key=None)
    if save_as_list:
        return documents
    return None

def txt_to_csv(input_file: str, output_file: str):
    """
    Convert a text file to a CSV file.

    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output CSV file.
    """
    # Open the input file for reading
    lines: list[str]
    with open(input_file, 'r', encoding="utf-8") as file:
        lines = file.readlines()

    # Process the lines and convert them to CSV format
    csv_lines = []
    for line in lines:
        # Split the line into fields (assuming comma-separated values)
        fields = line.strip().split(',')

        # Add the fields to the CSV lines
        csv_lines.append(','.join(fields))

    # Open the output file for writing
    with open(output_file, 'w', encoding="utf-8") as file:
        # Write the CSV lines to the output file
        file.write('\n'.join(csv_lines))
