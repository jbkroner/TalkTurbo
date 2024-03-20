from TalkTurbo import ChatContext
from TalkTurbo.ApiAdapters.ApiAdapter import ApiAdapter
from TalkTurbo.ApiAdapters.ModelDescription import ModelDescription

from anthropic import Anthropic
from anthropic.types.message import Message as AnthropicMessage


from TalkTurbo.Messages import (
    ContentMessage,
    MessageFactory,
    MessageRole,
    SystemMessage,
)


class AnthropicAdapter(ApiAdapter):
    def __init__(
        self,
        api_token: str,
        models: list[ModelDescription] = None,
    ):

        models = models or [
            ModelDescription(
                model_name="claude-3-opus-20240229",
                max_input_tokens=200000,
                max_output_tokens=4096,
            ),
            ModelDescription(
                model_name="claude-3-sonnet-20240229",
                max_input_tokens=200000,
                max_output_tokens=4096,
            )
            ModelDescription(
                model_name="claude-3-haiku-20240307",
                max_input_tokens=200000,
                max_output_tokens=4096,
            )
        ]

        super().__init__(api_token=api_token, models=models)

        self._anthropic_client = Anthropic(api_key=self._api_token)

    def get_chat_completion(self, context: ChatContext) -> ContentMessage:
        cleaned_context = self._remove_system_messages_from_context(
            context.get_messages_as_list()
        )
        completion = self._anthropic_client.messages.create(
            max_tokens=1024, messages=cleaned_context, model=self.models[0].model_name
        )

        if not completion:
            return SystemMessage(
                "_(turbo's host here: turbo didn't have anything to say :bluefootbooby:)_"
            )

        message, role = self._get_content_and_role_from_anthropic_message(completion)

        return MessageFactory.create_message(message, role)

    def _get_content_and_role_from_anthropic_message(
        self, anthropic_message: AnthropicMessage
    ) -> tuple[str, str]:
        return anthropic_message.content[0].text, anthropic_message.role

    def _remove_system_messages_from_context(self, messages: list) -> list:
        return [
            message for message in messages if message["role"] in {"user", "assistant"}
        ]
