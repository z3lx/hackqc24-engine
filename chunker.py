import csv
from langchain_text_splitters import TokenTextSplitter
from langchain.docstore.document import Document
import json
import os

def get_documents() -> list[Document]:
    """
    Turns all unchunked Documents in "chunks" project directory into a list of Documents in memory.
    
    Returns
        list[Document]: List of unchunked Documents, to have it in memory.
    """
    
    documents = []
    for index, file in enumerate(os.listdir("chunks")):
        page_content = ""
        metadeta = {}
        file_extension = (file.split(sep="."))[-1]
        current_file = f"chunks/{os.listdir("chunks")[index]}"
        
        if file_extension == "meta": 
            next_file = f"chunks/{os.listdir("chunks")[index+1]}"
            with open(current_file, "r", encoding="utf-8") as f:
                json_string = f.read()
                metadeta = json.loads(json_string)
            with open(next_file, "r", encoding="utf-8") as f:
                page_content = f.read()
                document = Document(page_content=page_content)
                document.metadata = metadeta
                documents.append(document)
            
    return documents
            
def chunk(documents: list[Document], save_as_file:bool, save_as_list:bool) -> list[Document]:
    """
    Chunks a list of unchunked Documents into chunked Documents
    
    Args:
        documents (list[Document]): List of unchunked Documents we want to chunk.
        save_as_file (boolean): Says if we want to write all the chunks as txt and json files, writes in "chunks" project directory.
        save_as_list (boolean): Says if we want to save all the chunks as a list of Documents in memory.
        
    Returns:
        list[Document]: A list of Documents if save_as_list is true, returns Nothing otherwise.
    """
    
    # Remove everything in "chunks" project folder
    for file in os.listdir("chunks"):
        os.remove(f"chunks/{file}")
    
    text_splitter = TokenTextSplitter()
    text_splitter._chunk_size = 4096
    text_splitter._chunk_overlap = 20
    document_split = text_splitter.split_documents(documents)

    if save_as_file:
        for index, document in enumerate(document_split):
            with open(f"chunks/chunk{index}.txt", "w", encoding="utf-8") as f:
                f.write(document.page_content)
            with open(f"chunks/chunk{index}.meta", "w", encoding="utf-8") as f:
                json.dump(document.metadata, f, ensure_ascii=False)
                # Print progress
            print(f"Document {index+1}/{len(document_split)} created       {round(((index+1)/len(document_split) * 100), 2)}% Done")
            
    if save_as_list:
        return document_split
    
    return None
