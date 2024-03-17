from TalkTurbo.ApiAdapters.ApiAdapter import ApiAdapter

import google.generativeai as genai

from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import AssistantMessage, ContentMessage, MessageRole


class GoogleAdapter(ApiAdapter):
    def __init__(self, api_token: str):
        super().__init__(api_token=api_token)
        self._api_token = api_token
        self._model_name = "gemini-pro"
        genai.configure(api_key=self._api_token)
        self._google_client = genai.GenerativeModel(model_name=self._model_name)

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
