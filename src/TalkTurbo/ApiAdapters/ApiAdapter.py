"""Generic interface for interacting with LLM SDKs"""

from TalkTurbo.Messages import ContentMessage
from TalkTurbo.ChatContext import ChatContext
from abc import ABC, abstractmethod


class ApiAdapter(ABC):
    @property
    @abstractmethod
    def _token(self) -> str:
        pass

    @_token.setter
    @abstractmethod
    def _token(self, value: str) -> None:
        pass

    @abstractmethod
    def get_chat_completion(context: ChatContext) -> ContentMessage:
        pass
