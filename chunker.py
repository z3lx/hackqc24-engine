import json
import os

from langchain.docstore.document import Document
from langchain_text_splitters import TokenTextSplitter


def chunk(path: str, documents: list[Document], save_as_file:bool, save_as_list:bool) -> list[Document]:
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
