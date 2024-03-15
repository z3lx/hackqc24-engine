from operator import itemgetter
from typing import Dict

import langchain_community.vectorstores as vectorstores
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from utils.history import MessageHistory


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
            ("system", "You are hackqc24-bot, a news summarizer, providing concise and objective summaries of current "
                       "events and important news stories from Quebec. Answer users with the help of provided context, "
                       "containing the most relevant and up-to-date information. When answering factual questions, or "
                       "questions about events, do not invent new information if the answer is not within the context. "
                       "Engage in conversation and provide information in a way that is easy to understand. Use an "
                       "informative but friendly tone and address the user by their username."),
            MessagesPlaceholder(variable_name="history"),
            ("system", "Retrieved context:\n{context}\n\nReturn the sources as links of the provided documents."),
            ("user", "{role}: {content}")
        ])

        self.main = (
            {
                "context": itemgetter("content") | self.retriever,
                "role": itemgetter("role"),
                "content": itemgetter("content")
            }
            | RunnablePassthrough.assign(
                history=RunnableLambda(self.history.load_messages) | itemgetter("history")
            )
            | self.prompt
            | self.model
        )

        self.add_human_message = (
            {"role": itemgetter("role"), "content": itemgetter("content")}
            | RunnableLambda(self._add_human_message)
        )

        self.add_ai_message = (
            itemgetter("content")
            | RunnableLambda(self._add_ai_message)
        )

    def _add_human_message(self, _dict: Dict[str, str]) -> str:
        role = _dict["role"]
        content = _dict["content"]
        self.history.add_human_message(content=f"{role}: {content}")
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
