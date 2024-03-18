from TalkTurbo import ChatContext
from TalkTurbo.ApiAdapters.ApiAdapter import ApiAdapter
from TalkTurbo.Messages import ContentMessage, SystemMessage, MessageFactory

from openai import OpenAI

import logging


class OpenAIAdapter(ApiAdapter):
    def __init__(
        self, api_token: str, logger: logging.Logger = logging.getLogger(__package__)
    ):
        super().__init__(api_token=api_token)
        self._logger = logger
        self._model = "gpt-3.5-turbo"
        self._open_ai_client = OpenAI(api_key=self._api_token)

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
            messages=context.get_messages_as_list(), model=self._model
        )

        if not completion:
            return SystemMessage(
                "_(turbo's host here: turbo didn't have anything to say :bluefootbooby:)_"
            )

        response = completion.choices[0].message

        return MessageFactory.create_message(response.content, response.role)
