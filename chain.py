from operator import itemgetter
from typing import Dict, Any

import langchain_community.vectorstores as vectorstores
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from history import MessageHistory


class ChatBot:
    def __init__(self, model_name: str, embeddings_model_name: str,
                 db_type: str, db_path: str, search_type: str = "mmr",
                 search_kwargs: Dict[str, any] = None) -> None:
        self.model = ChatOpenAI(model=model_name)
        self.embeddings = OpenAIEmbeddings(model=embeddings_model_name)
        self.history = MessageHistory(history_key="history")
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
            #("system", "Answer the user with the following context:\n{context}\n\n"
            #           "If the answer is not within the context or the history, "
            #           "do not invent new information and let the user know."),
            ("user", "{message}")
        ])

        self.main = (
            {"context": self.retriever,
             "message": RunnablePassthrough(),
             }
            | RunnablePassthrough.assign(
                history=RunnableLambda(self.history.load_messages) | itemgetter("history")
            )
            | self.prompt
            | self.model
        )

        self.add_human_message = (
            itemgetter("content")
            | RunnableLambda(self._add_human_message)
        )

        self.add_ai_message = (
            itemgetter("content")
            | RunnableLambda(self._add_ai_message)
        )

    def _add_human_message(self, content: str) -> str:
        self.history.add_human_message(content=content)
        return ""

    def _add_ai_message(self, content: str) -> str:
        self.history.add_ai_message(content=content)
        return ""

    def get_response(self, message: str) -> str:
        response = self.main.invoke(message).content
        self.history.add_human_message(content=message)
        self.history.add_ai_message(content=response)
        return response

    def get_main(self):
        return self.main

    def get_add_human_message(self):
        return self.add_human_message

    def get_add_ai_message(self):
        return self.add_ai_message
