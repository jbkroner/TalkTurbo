"""Generic interface for interacting with LLM SDKs"""

from TalkTurbo.Messages import AssistantMessage, SystemMessage
from TalkTurbo.ChatContext import ChatContext
from abc import ABC, abstractmethod


class ApiAdapter(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @property
    @abstractmethod
    def api_key(self) -> str:
        pass

    @api_key.setter
    @abstractmethod
    def api_key(self, value: str) -> None:
        pass

    @abstractmethod
    def get_chat_completion(context: ChatContext) -> AssistantMessage | SystemMessage:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass

    @abstractmethod
    def get_model_description(self) -> str:
        pass

    @abstractmethod
    def get_supported_message_types(self) -> list[str]:
        pass
