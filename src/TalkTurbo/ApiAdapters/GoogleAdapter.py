from TalkTurbo.ApiAdapters.ApiAdapter import ApiAdapter

import google.generativeai as genai

from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import AssistantMessage, ContentMessage, MessageFactory


class GoogleAdapter(ApiAdapter):
    def __init__(self, api_token: str):
        super().__init__(api_token=api_token)
        self._api_token = api_token
        self._model_name = "gemini-pro"
        genai.configure(api_key=self._api_token)
        print(genai)
        self._google_client = genai.GenerativeModel(model_name=self._model_name)

    def get_chat_completion(self, context: ChatContext) -> ContentMessage:
        response = self._google_client.generate_content("hey there")

        return AssistantMessage(content=response.text)
