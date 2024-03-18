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

    @abstractmethod
    def convert_context_to_api_format(self, context: ChatContext) -> list[dict]:
        """
        This method must be implemented by the child class to convert
        the ChatContext to the format expected by the relevant API.

        Args:
            context: A ChatContext object.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a message
            in the context, formatted for the relevant API.
        """
        pass
