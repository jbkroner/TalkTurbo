from TalkTurbo import ChatContext
from TalkTurbo.ApiAdapters.ApiAdapter import ApiAdapter

from anthropic import Anthropic

import logging

from TalkTurbo.Messages import ContentMessage, MessageFactory, SystemMessage


class AnthropicAdapter(ApiAdapter):
    def __init__(
        self, token: str, logger: logging.Logger = logging.getLogger(__package__)
    ):
        self._api_token = token
        self._logger = logger
        print(self._api_token)
        self._model = "claude-3-opus-20240229"
        self._anthropic_client = Anthropic(api_key=self._api_token)

    @property
    def _token(self) -> str:
        return self._api_token

    @_token.setter
    def _token(self, value: str) -> None:
        self._token = value

    def get_chat_completion(self, context: ChatContext) -> ContentMessage:
        cleaned_context = self._remove_system_messages_from_context(
            context.get_messages_as_list()
        )
        completion = self._anthropic_client.messages.create(
            max_tokens=1024, messages=cleaned_context, model=self._model
        )

        if not completion:
            return SystemMessage(
                "_(turbo's host here: turbo didn't have anything to say :bluefootbooby:)_"
            )

        return MessageFactory.create_message(completion.content, completion.role)

    def _remove_system_messages_from_context(self, messages: list) -> list:
        return [
            message for message in messages if message["role"] in {"user", "assistant"}
        ]
