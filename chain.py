from operator import itemgetter
from typing import Dict

from langchain.memory import ConversationBufferMemory
import langchain_community.vectorstores as vectorstores
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


class ChatBot:
    def __init__(self, model_name: str, embeddings_model_name: str,
                 db_type: str, db_path: str, search_type: str = "mmr", search_kwargs: Dict[str, any] = None) -> None:
        self.model = ChatOpenAI(model=model_name)
        self.embeddings = OpenAIEmbeddings(model=embeddings_model_name)
        self.memory = ConversationBufferMemory(return_messages=True)
        self.db = getattr(vectorstores, db_type)(
            persist_directory=db_path,
            embedding_function=self.embeddings
        )
        self.retriever = self.db.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )
        self.prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="history"),
            ("system", "Answer the user with the following context:\n{context}\n\n"
                       "If the answer is not within the context, do not invent new information and let the user know."),
            ("user", "{message}")
        ])
        self.chain = (
            {"context": self.retriever,
             "message": RunnablePassthrough(),
             }
            | RunnablePassthrough.assign(
                history=RunnableLambda(self.memory.load_memory_variables) | itemgetter("history")
            )
            | self.prompt
            | self.model
        )

    def get_response(self, message: str) -> str:
        response = self.chain.invoke(message).content
        self.memory.save_context(
            inputs={"input": message},
            outputs={"output": response}
        )
        return response
