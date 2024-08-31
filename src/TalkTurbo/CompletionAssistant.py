"""
The CompletionAssistant class is responsible for managing the API adapters and
providing a unified interface for interacting with them.
"""

from TalkTurbo.ApiAdapters.ApiAdapter import ApiAdapter
from TalkTurbo.ChatContext import ChatContext


class CompletionAssistant:
    """Class for managing the API adapters and providing a unified interface for interacting with them."""

    ADAPTER = None
    INITIALIZED = None

    @staticmethod
    def set_adapter(adapter: ApiAdapter):
        """
        Set the adapter to use for getting chat completions.

        Args:
            adapter: Instance of ApiAdapter to use for getting chat completions.

        """
        CompletionAssistant.ADAPTER = adapter
        CompletionAssistant.INITIALIZED = True

    @staticmethod
    def get_chat_completion(
        context: ChatContext, adapter: ApiAdapter = None
    ) -> ChatContext:
        """
        Get a chat completion from the adapter.

        Updates the context with the response from the adapter.
        """
        if not CompletionAssistant.INITIALIZED:
            raise RuntimeError(
                "CompletionAssistant has not been initialized. Please set the adapter first."
            )

        # use the static adapter if one is not passed in
        if not adapter:
            adapter = CompletionAssistant.ADAPTER

        response = adapter.get_chat_completion(context)

        context.add_message(response)

        return context
