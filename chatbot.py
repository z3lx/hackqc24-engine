from operator import itemgetter
from typing import Dict, Union

import langchain_community.vectorstores as vectorstores
from langchain_core.messages import BaseMessage
from langchain_core.prompt_values import ChatPromptValue
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
            (
                "system",
                "You are hackqc24-bot, a news summarizer, providing concise and objective summaries of current "
                "events and important news stories from Quebec. Answer users with the help of provided context, "
                "containing the most relevant and up-to-date information. When answering factual questions, or "
                "questions about events, do not invent new information if the answer is not within the context. "
                "Engage in conversation and provide information in a way that is easy to understand. Use an "
                "informative but friendly tone and address the user by their username."
            ),
            MessagesPlaceholder(variable_name="history"),
            (
                "system",
                "Retrieved context:\n{context}\n\nReturn the sources as links of the provided documents."
            ),
            (
                "user",
                "{role}: {content}"
            )
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
            | RunnableLambda(self._add_message)  # Save user response to history
            | self.model
            | RunnableLambda(self._add_message)  # Save AI response to history
        )

    def _add_message(self, input: Union[BaseMessage, ChatPromptValue]) \
            -> Union[BaseMessage, ChatPromptValue]:
        message = None
        if isinstance(input, BaseMessage):
            message = input
        elif isinstance(input, ChatPromptValue):
            message = input.to_messages()[-1]
        if message:
            self.history.add_message(message)
        return input

    def get_response(self, message: str) -> str:
        response = self.main.invoke({"role": "user", "content": message}).content
        return response

    def get_main(self):
        return self.main
