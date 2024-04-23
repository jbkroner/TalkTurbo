"""Generic interface for interacting with LLM SDKs"""

from abc import ABC, abstractmethod

from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import ContentMessage


class ApiAdapter(ABC):
    """Generic interface for interacting with LLM SDKs"""

    def __init__(self, api_token, model_name, max_tokens) -> None:
        super().__init__()
        self.api_token = api_token
        self.max_tokens = max_tokens
        self.model_name = model_name

    @abstractmethod
    def get_chat_completion(self, context: ChatContext) -> ContentMessage:
        """
        This method must be implemented by the child class to get a chat completion.

        Args:
            context: A ChatContext object.

        Returns:
            ContentMessage: The response content.
        """

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
