import json
import os

from langchain_core.documents import Document


def get_documents(path: str) -> list[Document]:
    """
    Reads all text and its associated metadata files from a given directory and returns a list of Document objects.

    Args:
        path (str): The path to the directory containing the text files.

    Returns:
        list[Document]: A list of Document objects representing the text files and its associated metadata.

    Raises:
        ValueError: If the provided path does not exist or if there is an error in reading the files.
    """
    if not os.path.exists(path):
        raise ValueError(f"Path {path} does not exist")
    try:
        docs = []
        for f in os.listdir(path):
            if not f.endswith(".txt"):
                continue
            with open(os.path.join(path, f), "r", encoding="utf-8") as file:
                page_content = file.read()
            with open(os.path.join(path, f"{f}.meta"), "r", encoding="utf-8") as meta_file:
                metadata = json.load(meta_file)
                if "source" not in metadata:
                    metadata["source"] = f
            docs.append(Document(page_content=page_content, metadata=metadata))
    except Exception as e:
        raise ValueError(f"Failed to load documents from {path}: {e}")
    return docs


def save_documents(path: str, documents: list[Document]) -> None:
    """
    Saves a list of Document objects to a specified directory. Each Document object is saved as two files:
    a text file containing the page content and a metadata file in JSON format.

    Args:
        path (str): The directory where the Document objects will be saved.
        documents (list[Document]): A list of Document objects to be saved.
    """
    os.makedirs(path, exist_ok=True)
    for i, doc in enumerate(documents):
        source = doc.metadata["source"].split('.')[0]
        with open(os.path.join(path, f"{source}.{i}.txt"), "w", encoding="utf-8") as file:
            file.write(doc.page_content)
        with open(os.path.join(path, f"{source}.{i}.txt.meta"), "w", encoding="utf-8") as meta_file:
            json.dump(doc.metadata, meta_file, ensure_ascii=False)
