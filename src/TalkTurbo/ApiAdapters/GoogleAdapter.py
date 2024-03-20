from TalkTurbo.ApiAdapters.ApiAdapter import ApiAdapter

import google.generativeai as genai

from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import AssistantMessage, ContentMessage, MessageRole
from TalkTurbo.ApiAdapters.ModelDescription import ModelDescription


class GoogleAdapter(ApiAdapter):
    def __init__(self, api_token: str, models: list[ModelDescription] = None):
        models = models or [
            ModelDescription(
                model_name="gemini-pro", max_input_tokens=2048, max_output_tokens=2048
            )
        ]

        super().__init__(api_token=api_token)
        genai.configure(api_key=self._api_token)

        self._google_client = genai.GenerativeModel(
            model_name=self.models[0].model_name
        )

    def get_chat_completion(self, context: ChatContext) -> ContentMessage:
        google_context = self.chat_context_to_google_format(context)
        response = self._google_client.generate_content(google_context)

        return AssistantMessage(content=response.text)

    def chat_context_to_google_format(self, context: ChatContext):
        return [
            {"role": message.role.value, "parts": [message.content]}
            for message in context.messages
            if message.role in [MessageRole.USER, MessageRole.ASSISTANT]
        ]
