from typing import List, Dict, Any

from langchain_core.messages import (
    BaseMessage, AIMessage, HumanMessage, ChatMessage, SystemMessage, FunctionMessage, ToolMessage
)


class MessageHistory:
    def __init__(self, history_key: str = "history",
                 message_limit: int = 100) -> None:
        self.messages: List[BaseMessage] = []
        self.message_limit = message_limit
        self.history_key = history_key

    def load_messages(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {"history": self.get_messages()}

    def get_messages(self) -> List[BaseMessage]:
        return self.messages

    def add_message(self, message: BaseMessage) -> None:
        self.messages.append(message)
        if len(self.messages) > self.message_limit:
            self.messages = self.messages[-self.message_limit:]

    def add_ai_message(self, content: str) -> None:
        self.add_message(AIMessage(content=content))

    def add_human_message(self, content: str) -> None:
        self.add_message(HumanMessage(content=content))

    def add_chat_message(self, content: str, role: str) -> None:
        self.add_message(ChatMessage(content=content, role=role))

    def add_system_message(self, content: str) -> None:
        self.add_message(SystemMessage(content=content))

    def add_function_message(self, content: str) -> None:
        self.add_message(FunctionMessage(content=content))

    def add_tool_message(self, content: str) -> None:
        self.add_message(ToolMessage(content=content))

    def clear(self) -> None:
        self.messages = []
