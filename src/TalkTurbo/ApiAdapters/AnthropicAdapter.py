from anthropic import Anthropic
from anthropic.types.message import Message as AnthropicMessage

from TalkTurbo import ChatContext
from TalkTurbo.ApiAdapters import ApiAdapter
from TalkTurbo.Messages import ContentMessage, MessageFactory, SystemMessage


class AnthropicAdapter(ApiAdapter):
    """Adapter for Anthropic's API."""

    def __init__(
        self,
        api_token: str,
        max_tokens: int = 1024,
        model_name: str = "claude-3-opus-20240229",
    ):
        super().__init__(api_token=api_token, model_name=model_name, max_tokens=1024)
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
        return self._remove_system_messages_from_context(context.get_messages_as_list())

    def _get_content_and_role_from_anthropic_message(
        self, anthropic_message: AnthropicMessage
    ) -> tuple[str, str]:
        return anthropic_message.content[0].text, anthropic_message.role

    def _remove_system_messages_from_context(self, messages: list) -> list:
        return [
            message for message in messages if message["role"] in {"user", "assistant"}
        ]
