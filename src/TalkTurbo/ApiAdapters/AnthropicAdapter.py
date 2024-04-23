"""Adapter for Anthropic's API."""

from anthropic import Anthropic
from anthropic.types.message import Message as AnthropicMessage

from TalkTurbo.ApiAdapters.ApiAdapter import ApiAdapter
from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import ContentMessage, MessageFactory, SystemMessage


class AnthropicAdapter(ApiAdapter):
    """Adapter for Anthropic's API."""

    AVAILABLE_MODELS = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]

    def __init__(
        self,
        api_token: str,
        max_tokens: int = 4096,
        model_name: str = "claude-3-opus-20240229",
    ):
        super().__init__(
            api_token=api_token, model_name=model_name, max_tokens=max_tokens
        )
        self._anthropic_client = Anthropic(api_key=self.api_token)

    def get_chat_completion(self, context: ChatContext) -> ContentMessage:
        cleaned_context = self.convert_context_to_api_format(context)

        completion = self._anthropic_client.messages.create(
            max_tokens=1024, messages=cleaned_context, model=self.model_name
        )

        if not completion:
            return SystemMessage(
                "_(turbo's host here: turbo didn't have anything to say :bluefootbooby:)_"
            )

        message, role = self._get_content_and_role_from_anthropic_message(completion)

        return MessageFactory.create_message(message, role)

    def convert_context_to_api_format(self, context: ChatContext):
        messages = [
            {"content": "(ignore this message)", "role": "user"}
        ] + context.get_messages_as_list()
        return self._remove_system_messages_from_context(messages)

    def _get_content_and_role_from_anthropic_message(
        self, anthropic_message: AnthropicMessage
    ) -> tuple[str, str]:
        return anthropic_message.content[0].text, anthropic_message.role

    def _remove_system_messages_from_context(
        self, messages: list[ContentMessage]
    ) -> list:
        """convert any system messages to user messages"""
        for message in messages:
            if message["role"] == "system":
                message["role"] = "assistant"

        return messages
