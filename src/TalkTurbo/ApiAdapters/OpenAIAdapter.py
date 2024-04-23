import logging

from openai import OpenAI

from TalkTurbo import ChatContext
from TalkTurbo.ApiAdapters.ApiAdapter import ApiAdapter
from TalkTurbo.Messages import ContentMessage, MessageFactory, SystemMessage


class OpenAIAdapter(ApiAdapter):
    """Adapter for OpenAI's API."""

    AVAILABLE_MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]

    def __init__(
        self,
        api_token: str,
        model_name: str = "gpt-3.5-turbo",
        max_tokens=1024,
    ):
        super().__init__(
            api_token=api_token, model_name=model_name, max_tokens=max_tokens
        )
        self._open_ai_client = OpenAI(api_key=self.api_token)

    def get_chat_completion(self, context: ChatContext) -> ContentMessage:
        """
        Get a chat completion for a given ChatContext.

        This method expects that messages in the context have been moderated.

        This method does not modify the given ChatContext.

        Args:
            context: The context of the chat.

        Returns:
            ContentMessage: The response content or an error string informing the user that
            Something went wrong with the request.
        """
        completion = self._open_ai_client.chat.completions.create(
            messages=context.get_messages_as_list(), model=self.model_name
        )

        if not completion:
            return SystemMessage(
                "_(turbo's host here: turbo didn't have anything to say :bluefootbooby:)_"
            )

        response = completion.choices[0].message

        return MessageFactory.create_message(response.content, response.role)

    def convert_context_to_api_format(self, context: ChatContext):
        return context.get_messages_as_list()
