import argparse

from langchain.docstore.document import Document
from langchain_text_splitters import TokenTextSplitter


def chunk(documents: list[Document],
          chunk_size: int = 4000, chunk_overlap: int = 200,
          model_name: str = "gpt-3.5-turbo-0125") -> list[Document]:
    """
    Splits a list of documents into chunks.

    This function takes a list of documents and splits each document into chunks of a specified size.
    The chunks can overlap, and the size of the overlap can also be specified.
    The function uses a specific model for splitting the documents.
    If a path is provided, the function will save the chunked documents to that path.

    Args:
        documents (list[Document]): The list of documents to be chunked.
        chunk_size (int, optional): The size of each chunk. Defaults to 4000.
        chunk_overlap (int, optional): The size of the overlap between chunks. Defaults to 200.
        model_name (str, optional): The name of the LLM to select the encoding for the token counter.
            Defaults to "gpt-3.5-turbo-0125".

    Returns:
        list[Document]: The list of chunked documents.
    """
    splitter = TokenTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        model_name=model_name,
    )
    return splitter.split_documents(documents)


if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.document import get_documents, save_documents

    parser = argparse.ArgumentParser(description="Splits a list of documents into chunks.")
    parser.add_argument("--input", type=str, required=True,
                        help="The input directory containing the documents.")
    parser.add_argument("--output", type=str, required=True,
                        help="The output directory to save the chunked documents.")
    parser.add_argument("--chunk-size", type=int, default=4000,
                        help="The size of each chunk.")
    parser.add_argument("--chunk-overlap", type=int, default=200,
                        help="The size of the overlap between chunks.")
    parser.add_argument("--model-name", type=str, default="gpt-3.5-turbo-0125",
                        help="The name of the LLM to select the encoding for the token counter.")

    args = parser.parse_args()

    docs = get_documents(path=args.input)
    docs = chunk(docs, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap, model_name=args.model_name)
    save_documents(path=args.output, documents=docs)
