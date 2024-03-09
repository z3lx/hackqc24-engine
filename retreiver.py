import os

from langchain_community.vectorstores.chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

os.environ["LANGCHAIN_TRACING_V2"] = "true"

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
model = ChatOpenAI(model="gpt-3.5-turbo-0125")

db = Chroma(
    persist_directory="./chromadb",
    embedding_function=embeddings
)
retriever = db.as_retriever(search_kwargs={"k": 1})
# docs = db.similarity_search(question)

template = """Answer the question with the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

while True:
    question = input("")
    answer = chain.invoke(question)
    print(answer)
