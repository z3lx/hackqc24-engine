import argparse
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


if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.document import get_documents, save_documents

    parser = argparse.ArgumentParser(description="Filter documents metadata.")
    parser.add_argument("--input", type=str, required=True,
                        help="The input directory containing the documents.")
    parser.add_argument("--output", type=str, required=True,
                        help="The output directory to save the filtered documents.")
    parser.add_argument("--keys", type=str, nargs='+', required=True,
                        help="The keys to keep in the metadata.")

    args = parser.parse_args()

    docs = get_documents(path=args.input)
    docs = filter_metadata(docs=docs, keys=args.keys)
    save_documents(path=args.output, documents=docs)
