"""Adapter for Groq's API."""

from groq import Groq

from TalkTurbo.ApiAdapters.ApiAdapter import ApiAdapter
from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import ContentMessage, MessageFactory, SystemMessage


class GroqAdapter(ApiAdapter):
    """Adapter for Groq's API."""

    # https://console.groq.com/docs/models
    AVAILABLE_MODELS = [
        "llama3-8b-8192",  # meta
        "llama3-70b-8192",  # meta
        "mixtral-8x7b-32768",  # mistral
        "gemma-7b-it",  # google
    ]

    def __init__(self, api_token, model_name=AVAILABLE_MODELS[0], max_tokens=4096) -> None:
        super().__init__(api_token=api_token, model_name=model_name, max_tokens=max_tokens)
        self._groq_client = Groq(api_key=self.api_token)

    def get_chat_completion(self, context: ChatContext) -> ContentMessage:
        completion = self._groq_client.chat.completions.create(
            messages=context.get_messages_as_list(), model=self.model_name
        )

        if not completion:
            return SystemMessage(
                "_(turbo's host here: turbo didn't have anything to say :bluefootbooby:)_"
            )

        response = completion.choices[0].message

        return MessageFactory.create_message(response.content, response.role)

    def convert_context_to_api_format(self, context: ChatContext):
        return [
            message
            for message in context.messages
            if message.role.value in ["user", "assistant", "system"]
        ]
