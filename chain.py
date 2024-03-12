import os
from operator import itemgetter

from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Language chain
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
     #"language": lang_chain
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
