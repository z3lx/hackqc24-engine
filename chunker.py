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
        path (str, optional): The path where the chunked documents will be saved. Defaults to None.
        chunk_size (int, optional): The size of each chunk. Defaults to 4000.
        chunk_overlap (int, optional): The size of the overlap between chunks. Defaults to 200.
        model_name (str, optional): The name of the model to be used for splitting the documents.
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
