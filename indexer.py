import json
import os
from typing import Union, List, Literal

from langchain.indexes import SQLRecordManager, index, IndexingResult
import langchain_community.vectorstores as vectorstores
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from langchain_core.documents.base import Document


def clear_index(db_path: str, db_type: str = "Chroma", namespace: str = None) -> None:
    update_index([], db_path=db_path, db_type=db_type, namespace=namespace, cleanup="full")


def update_index(docs: Union[List[Document], str],
                 db_path: str, db_type: str = "Chroma", namespace: str = None, source_key: str = "source",
                 embedding_function: Union[Embeddings, str] = OpenAIEmbeddings(model="text-embedding-3-small"),
                 cleanup: Union[Literal["incremental", "full"], None] = "full") -> IndexingResult:
    # Load documents
    if isinstance(docs, str):
        path = docs
        if not os.path.exists(path):
            raise ValueError(f"Path {path} does not exist")
        try:
            docs = [
                Document(
                    page_content=open(os.path.join(path, f), "r", encoding="utf-8").read(),
                    metadata=json.load(open(os.path.join(path, f"{f}.meta"), "r", encoding="utf-8"))
                ) for f in os.listdir(path) if f.endswith(".txt")
            ]
        except Exception as e:
            raise ValueError(f"Failed to load documents from {path}: {e}")
    elif not all(isinstance(doc, Document) for doc in docs):
        raise ValueError("docs must be a list of Document objects")

    # Create record manager
    os.makedirs(db_path, exist_ok=True)
    record_namespace = namespace if namespace is not None or str else f"{db_type.lower()}/indexing"
    record_path = os.path.join(db_path, "record_manager_cache.sql")
    record_manager = SQLRecordManager(
        namespace=record_namespace,
        db_url=f"sqlite:///{record_path}"
    )
    record_manager.create_schema()

    # Create embeddings
    try:
        if isinstance(embedding_function, str):
            embedding_function = OpenAIEmbeddings(model=embedding_function)
    except Exception as e:
        raise ValueError(f"Failed to create embedding function: {e}")

    # Create vector store
    try:
        vector_store = getattr(vectorstores, db_type)(
            persist_directory=db_path,
            embedding_function=embedding_function
        )
    except Exception as e:
        raise ValueError(f"Failed to create vector store: {e}")

    # Index documents
    return index(
        docs_source=docs,
        record_manager=record_manager,
        vector_store=vector_store,
        cleanup=cleanup,
        source_id_key=source_key
    )


if __name__ == "__main__":
    result = update_index(
        docs="./datasets/",
        db_path="./chromadb"
    )
    print(result)
