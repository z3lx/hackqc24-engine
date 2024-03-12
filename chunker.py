import csv
from langchain_text_splitters import TokenTextSplitter
from langchain.schema.document import Document
import json
import os

def get_documents(path: str) -> list[Document]:
    documents = []
    for index, file in enumerate(os.listdir(path)):
        page_content = ""
        metadeta = {}
        if (index % 2) == 0:
            with open(file, "r", encoding="utf-8") as f:
                page_content = f.read()
            with open(os.listdir[index + 1], "r", encoding="utf-8") as f:
                metadeta = json.load(f)
            documents.append(Document(page_content=page_content, metadeta))
                
            
def chunk(documents: list[Document]) -> None:
    """
    Chunks a list of Documents into smaller Documents
    
    Args:
        
        
    """
    
    for index, document in enumerate(documents):
        if (index % 2) == 0:
            with open()
        metadata = create_metadata(row=row, format=format)
        text_chunks = TokenTextSplitter(chunk_size=4096, chunk_overlap = 20).split_text(text=row[index_of_description])
        for text in text_chunks:
            documents.append(Document(page_content=text, metadata=metadata))
            
    

if __name__ == "__main__":
    first_dataset = parse_dataset("datasets\\Communiqués de presse\\Communiqués de presse (2023 à aujourd'hui).csv")
    documents = chunkAsDocument(dataset=first_dataset, format={"title":0,"publication date":1,"url":2,"district service":4,"source":5}, index_of_description=3)
