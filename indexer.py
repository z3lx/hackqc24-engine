import os

from langchain.indexes import SQLRecordManager, index
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from langchain_core.documents.base import Document

if __name__ == "__main__":
    # Demo docs
    docs = [
        Document(
            page_content=open("./datasets/accueil.txt", "r", encoding="utf-8").read(),
            metadata={"source": "accueil.txt"}
        ),
        Document(
            page_content=open("./datasets/apropos.txt", "r", encoding="utf-8").read(),
            metadata={"source": "apropos.txt"}
        )
    ]

    db_dir = "./chromadb"
    os.makedirs(db_dir, exist_ok=True)
    record_cache = os.path.join(db_dir, "record_manager_cache.sql")

    record_manager = SQLRecordManager(
        namespace="chromadb/demo_index",
        db_url=f"sqlite:///{record_cache}"
    )
    record_manager.create_schema()

    vectorstore = Chroma(
        persist_directory=db_dir,
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
    )

    result = index(
        docs_source=docs,
        record_manager=record_manager,
        vector_store=vectorstore,
        cleanup="full",
        source_id_key="source",
    )

    print(result)
