import os

from langchain_community.vectorstores.chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

os.environ["LANGCHAIN_TRACING_V2"] = "true"

lang_prompt = PromptTemplate.from_template(
    "What language is the following text written in?\n"
    "text=\"{text}\"\n"
    "Reply in a singular word."
)
lang_model = ChatOpenAI(
    model="gpt-3.5-turbo-0125",
    temperature=0
)
lang_chain = (
    {"text": RunnablePassthrough()}
    | lang_prompt
    | lang_model
    | StrOutputParser()
)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
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
Answer the question in {language}.
"""
prompt = ChatPromptTemplate.from_template(template)

chain = (
    {"context": retriever,
     "question": RunnablePassthrough(),
     "language": lang_chain
     }
    | prompt
    | model
    | StrOutputParser()
)

while True:
    question = input("")
    answer = chain.invoke(question)
    print(answer)
