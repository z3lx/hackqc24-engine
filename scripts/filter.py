from typing import List

from langchain_core.documents import Document


def filter_metadata(docs: List[Document], keys: List[str]) -> List[Document]:
    """
    Filters the metadata of a list of Document objects based on a list of keys.

    Args:
        docs (List[Document]): The list of Document objects.
        keys (List[str]): The list of keys to keep in the metadata.

    Returns:
        List[Document]: The filtered list of Document objects.
    """
    for doc in docs:
        doc.metadata = {k: v for k, v in doc.metadata.items() if k in keys}
    return docs
