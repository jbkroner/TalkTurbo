"""Generic interface for interacting with LLM SDKs"""

from TalkTurbo.Messages import ContentMessage
from TalkTurbo.ChatContext import ChatContext
from abc import ABC, abstractmethod


class ApiAdapter(ABC):
    def __init__(self, api_token) -> None:
        super().__init__()
        self._api_token = api_token

    @abstractmethod
    def get_chat_completion(self, context: ChatContext) -> ContentMessage:
        pass
