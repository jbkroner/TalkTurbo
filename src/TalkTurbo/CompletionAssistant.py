"""
The CompletionAssistant class is responsible for managing the API adapters and 
providing a unified interface for interacting with them.
"""

from TalkTurbo.ChatContext import ChatContext


class CompletionAssistant:
    """Class for managing the API adapters and providing a unified interface for interacting with them."""

    ADAPTER = None
    INITIALIZED = None

    @staticmethod
    def set_adapter(adapter):
        """Set the adapter to use for getting chat completions."""
        CompletionAssistant.ADAPTER = adapter
        CompletionAssistant.INITIALIZED = True

    @staticmethod
    def get_chat_completion(context: ChatContext) -> ChatContext:
        """
        Get a chat completion from the adapter.

        Updates the context with the response from the adapter.
        """
        response = CompletionAssistant.ADAPTER.get_chat_completion(context)

        context.add_message(response)

        return context
