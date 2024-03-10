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


    

if __name__ == "__main__":
    chunks = []
    
    first_dataset = parse_dataset("datasets\\Communiqués de presse\\Communiqués de presse (2023 à aujourd'hui).csv")
    
