import os
from operator import itemgetter

from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

os.environ["LANGCHAIN_TRACING_V2"] = "true"

model = ChatOpenAI(model="gpt-3.5-turbo-0125")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
memory = ConversationBufferMemory(return_messages=True)
db = Chroma(
    persist_directory="./chromadb",
    embedding_function=embeddings
)
retriever = db.as_retriever(search_kwargs={"k": 1})
# docs = db.similarity_search(question)

prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="history"),
    ("system", "Answer the user with the following context:\n{context}"),
    ("user", "{message}")
])

chain = (
    {"context": retriever,
     "message": RunnablePassthrough(),
     }
    | RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
    )
    | prompt
    | model
)

while True:
    message = input("")
    response = chain.invoke(message)
    memory.save_context(
        inputs={"input": message},
        outputs={"output": response.content}
    )
    print(response.content)
