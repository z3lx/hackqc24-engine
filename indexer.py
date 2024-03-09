from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from langchain_core.documents.base import Document

docs = [
    Document(page_content=open("./datasets/accueil.txt", "r", encoding="utf-8").read()),
    Document(page_content=open("./datasets/apropos.txt", "r", encoding="utf-8").read())
]

db = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(model="text-embedding-3-large"),
    persist_directory="./chromadb"
)
