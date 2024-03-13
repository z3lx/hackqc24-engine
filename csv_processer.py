import csv
from langchain.schema.document import Document
import web_scraper
from data_utils import save_txt

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
        metadata = create_metadata(row, format)
        page_content = row[index_of_description]
        if format["url"] is not None:
            index_of_url = format["url"]
            url = row[index_of_url]
            page_content += web_scraper.scrape_montreal(url)
        
        if save_as_file:
            save_txt(page_content, metadata, f"chunks/document{index}")
            print(f"Document {index+1}/{len(dataset)} created       {round(((index+1)/len(dataset) * 100), 2)}% Done")
                    
        if save_as_list:
            document = Document(page_content=page_content)
            document.metadata = metadata
            documents.append(document)
        
    if save_as_file:
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
